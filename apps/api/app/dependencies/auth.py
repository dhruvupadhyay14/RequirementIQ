from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_token
from app.exceptions.custom_exceptions import UnauthorizedException, UserNotFoundException
from app.models.user import User, UserRole


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException()

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise UnauthorizedException()

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise UserNotFoundException()
    return user


def get_current_company(user: User = Depends(get_current_user)):
    return user.company_id


def get_current_company_id(user: User = Depends(get_current_user)):
    return get_current_company(user)


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in [UserRole.SUPER_ADMIN, UserRole.COMPANY_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permissions required")
    return user
