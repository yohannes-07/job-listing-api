import uuid
from typing import Optional
from pydantic import BaseModel
from app.db.models import Role


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[uuid.UUID] = None
    role: Optional[Role] = None
