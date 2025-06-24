import re
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.db.models import Role


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, pattern=r"^[a-zA-Z\s]+$")
    email: EmailStr
    role: Role


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class User(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    name: str

    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str
