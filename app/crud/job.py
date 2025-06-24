from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.db.models import Job, User, Application
from app.schemas.job import JobCreate, JobUpdate
import uuid
from typing import Optional


def get_job(db: Session, id: uuid.UUID):
    return db.query(Job).options(joinedload(Job.owner)).filter(Job.id == id).first()


def get_jobs_query(
    db: Session,
    title: Optional[str] = None,
    location: Optional[str] = None,
    company_name: Optional[str] = None,
):
    query = db.query(Job).options(joinedload(Job.owner))
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if company_name:
        query = query.join(User).filter(User.name.ilike(f"%{company_name}%"))
    return query


def get_jobs_by_owner_query(db: Session, owner_id: uuid.UUID):
    application_count_subquery = (
        db.query(
            Application.job_id, func.count(Application.id).label("application_count")
        )
        .group_by(Application.job_id)
        .subquery()
    )

    return (
        db.query(Job, application_count_subquery.c.application_count)
        .outerjoin(
            application_count_subquery,
            Job.id == application_count_subquery.c.job_id,
        )
        .filter(Job.created_by == owner_id)
    )


def create_job(db: Session, job: JobCreate, owner_id: uuid.UUID):
    db_job = Job(**job.model_dump(), created_by=owner_id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job(db: Session, db_obj: Job, obj_in: JobUpdate):
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_job(db: Session, id: uuid.UUID):
    db_obj = db.query(Job).get(id)
    db.delete(db_obj)
    db.commit()
    return db_obj
