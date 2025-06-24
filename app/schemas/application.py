import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.db.models import ApplicationStatus
from .user import UserPublic
from .job import JobBase


class ApplicationBase(BaseModel):
    job_id: uuid.UUID
    cover_letter: Optional[str] = Field(None, max_length=200)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class Application(ApplicationBase):
    id: uuid.UUID
    applicant_id: uuid.UUID
    resume_link: str
    status: ApplicationStatus
    applied_at: datetime

    class Config:
        from_attributes = True


class ApplicationForApplicant(BaseModel):
    id: uuid.UUID
    status: ApplicationStatus
    applied_at: datetime
    job: JobBase

    class Config:
        from_attributes = True


class ApplicationForCompany(BaseModel):
    id: uuid.UUID
    resume_link: str
    cover_letter: Optional[str]
    status: ApplicationStatus
    applied_at: datetime
    applicant: UserPublic

    class Config:
        from_attributes = True
