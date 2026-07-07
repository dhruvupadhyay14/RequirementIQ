from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, ProfileUpdateRequest, RegisterRequest, ResetPasswordRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.validation.auth_validation import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(payload)


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh(refresh_token)


@router.get("/me", response_model=UserResponse)
def current_user(request: Request, db: Session = Depends(get_db)):
    current = get_current_user(request, db)
    return UserResponse.model_validate(current)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    return {"message": "Password reset link placeholder"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    return {"message": "Password reset placeholder"}


@router.put("/users/profile", response_model=UserResponse)
def update_profile(payload: ProfileUpdateRequest, request: Request, db: Session = Depends(get_db)):
    current = get_current_user(request, db)
    service = AuthService(db)
    return service.update_profile(str(current.id), payload)
