from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.apis.deps import get_db, get_current_applicant, get_current_company
from app.crud import application as crud_application, job as crud_job
from app.schemas.application import ApplicationForApplicant
from app.schemas.job import JobWithApplicationCount
from app.db.models import User
from fastapi_pagination import Page, paginate

router = APIRouter()


@router.get("/applications", response_model=Page[ApplicationForApplicant])
def read_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_applicant),
):
    """
    Retrieve applications for the current user.
    """
    applications_query = crud_application.get_applications_by_applicant_query(
        db, applicant_id=current_user.id
    )
    return paginate(applications_query)


def transform_job_with_application_count(job_tuple):
    job, count = job_tuple
    job_dict = {c.name: getattr(job, c.name) for c in job.__table__.columns}
    return JobWithApplicationCount(**job_dict, application_count=count or 0)


@router.get("/jobs", response_model=Page[JobWithApplicationCount])
def read_my_posted_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company),
):
    """
    Retrieve jobs posted by the current company.
    """
    jobs_query = crud_job.get_jobs_by_owner_query(db, owner_id=current_user.id)
    return paginate(jobs_query, transformer=transform_job_with_application_count)
