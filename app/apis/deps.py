from typing import Generator
from app.db.session import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core.config import settings
from app.schemas.token import TokenData
from app.crud import user as crud_user
from app.db.models import User, Role
import json

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(**json.loads(payload.get("sub")))
    except (JWTError, json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud_user.get_user(
        db, user_id=token_data.id
    )  # get_user by id is not implemented yet
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_company(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def get_current_applicant(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.applicant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
