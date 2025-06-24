import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .user import UserPublic


class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=20, max_length=2000)
    location: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    location: Optional[str] = None


class Job(JobBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class JobWithOwner(Job):
    owner: UserPublic


class JobWithApplicationCount(Job):
    application_count: int
