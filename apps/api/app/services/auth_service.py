from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.user import User, UserRole, UserStatus
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import LoginRequest, ProfileUpdateRequest, RegisterRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepository(db)
        self.db = db

    def register(self, payload: RegisterRequest) -> TokenResponse:
        if self.repository.get_user_by_email(payload.email.lower()):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        company = self.repository.create_company(payload.company_name, payload.industry)
        workspace = self.repository.create_workspace(company.id, payload.workspace_name)
        password_hash = self._hash_password(payload.password)
        user = self.repository.create_user(
            company_id=company.id,
            workspace_id=workspace.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email.lower(),
            password_hash=password_hash,
            phone=payload.phone,
            role=UserRole.COMPANY_ADMIN,
            status=UserStatus.ACTIVE,
        )
        self.repository.commit()

        access_token = self._create_token(user.id, "access")
        refresh_token = self._create_token(user.id, "refresh")
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=self._serialize_user(user))

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.repository.get_user_by_email(payload.email.lower())
        if not user or not self._verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not active")

        access_token = self._create_token(user.id, "access")
        refresh_token = self._create_token(user.id, "refresh")
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=self._serialize_user(user))

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

        user = self.db.query(User).filter(User.id == payload.get("sub")).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        access_token = self._create_token(user.id, "access")
        refresh_token = self._create_token(user.id, "refresh")
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=self._serialize_user(user))

    def me(self, user_id: str) -> UserResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return self._serialize_user(user)

    def update_profile(self, user_id: str, payload: ProfileUpdateRequest) -> UserResponse:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if payload.first_name is not None:
            user.first_name = payload.first_name
        if payload.last_name is not None:
            user.last_name = payload.last_name
        if payload.phone is not None:
            user.phone = payload.phone
        self.repository.update_user(user)
        self.repository.commit()
        return self._serialize_user(user)

    def forgot_password(self, email: str) -> dict[str, str]:
        return {"message": "Password reset link placeholder"}

    def reset_password(self, token: str, new_password: str) -> dict[str, str]:
        return {"message": "Password reset placeholder"}

    def _create_token(self, user_id, token_type: str) -> str:
        now = datetime.now(timezone.utc)
        expiry = now + (timedelta(minutes=15) if token_type == "access" else timedelta(days=7))
        payload = {"sub": str(user_id), "token_type": token_type, "exp": expiry}
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def _serialize_user(self, user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            company_id=user.company_id,
            workspace_id=user.workspace_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone,
            role=user.role.value,
            status=user.status.value,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
