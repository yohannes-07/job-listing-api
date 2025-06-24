from sqlalchemy.orm import Session, joinedload
from app.db.models import Application, Job
from app.schemas.application import ApplicationCreate
import uuid


def get_applications_by_applicant_query(db: Session, applicant_id: uuid.UUID):
    return (
        db.query(Application)
        .filter(Application.applicant_id == applicant_id)
        .options(joinedload(Application.job).joinedload(Job.owner))
    )


def get_applications_by_job_id_query(db: Session, job_id: uuid.UUID):
    return (
        db.query(Application)
        .filter(Application.job_id == job_id)
        .options(joinedload(Application.applicant))
    )


def create_application(
    db: Session,
    application: ApplicationCreate,
    applicant_id: uuid.UUID,
    resume_link: str,
):
    db_application = Application(
        **application.model_dump(), applicant_id=applicant_id, resume_link=resume_link
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def get_application_by_applicant_and_job(
    db: Session, applicant_id: uuid.UUID, job_id: uuid.UUID
):
    return (
        db.query(Application)
        .filter(Application.applicant_id == applicant_id, Application.job_id == job_id)
        .first()
    )


def get_application(db: Session, id: uuid.UUID):
    return db.query(Application).options(joinedload(Application.job)).filter(Application.id == id).first()


def update_application_status(db: Session, db_obj: Application, status: str):
    db_obj.status = status
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
