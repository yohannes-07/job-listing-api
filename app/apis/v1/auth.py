from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.apis.deps import get_db
from app.schemas.user import UserCreate, User
from app.schemas.token import Token
from app.schemas.base import BaseResponse
from app.crud import user as crud_user
from app.core.security import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
import json

router = APIRouter()


@router.post("/signup", response_model=BaseResponse[User])
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    created_user = crud_user.create_user(db=db, user=user)
    return BaseResponse(object=created_user, message="User created successfully")


@router.post("/login", response_model=BaseResponse[Token])
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"id": str(user.id), "role": user.role.value}
    access_token = create_access_token(subject=json.dumps(token_data))

    token = Token(access_token=access_token, token_type="bearer")
    return BaseResponse(object=token, message="Login successful")
