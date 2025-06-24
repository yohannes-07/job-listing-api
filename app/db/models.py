import uuid
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import enum
from datetime import datetime

Base = declarative_base()


class Role(str, enum.Enum):
    applicant = "applicant"
    company = "company"


class ApplicationStatus(str, enum.Enum):
    applied = "Applied"
    reviewed = "Reviewed"
    interview = "Interview"
    rejected = "Rejected"
    hired = "Hired"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)

    jobs = relationship("Job", back_populates="owner")
    applications = relationship("Application", back_populates="applicant")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(100), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    resume_link = Column(String, nullable=False)
    cover_letter = Column(Text, nullable=True)
    status = Column(
        Enum(ApplicationStatus), default=ApplicationStatus.applied, nullable=False
    )
    applied_at = Column(DateTime, default=datetime.utcnow)

    applicant = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
