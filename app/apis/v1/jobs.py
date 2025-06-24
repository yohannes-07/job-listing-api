from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.apis.deps import (
    get_db,
    get_current_company,
    get_current_applicant,
    get_current_user,
)
from app.schemas.job import JobCreate, JobUpdate, Job, JobWithOwner
from app.schemas.base import BaseResponse
from app.crud import job as crud_job
from app.db.models import User
import uuid
from typing import Optional
from fastapi_pagination import Page, paginate
from . import applications

router = APIRouter()
router.include_router(
    applications.router, prefix="/{job_id}/applications", tags=["applications"]
)


@router.get("/", response_model=Page[JobWithOwner])
def read_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_applicant),
    title: Optional[str] = None,
    location: Optional[str] = None,
    company_name: Optional[str] = None,
):
    """
    Retrieve jobs with filters and pagination.
    """
    jobs_query = crud_job.get_jobs_query(
        db, title=title, location=location, company_name=company_name
    )
    return paginate(jobs_query)


@router.get("/{id}", response_model=BaseResponse[JobWithOwner])
def read_job(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    id: uuid.UUID,
):
    """
    Get job by ID.
    """
    job = crud_job.get_job(db, id=id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return BaseResponse(object=job)


@router.post("/", response_model=BaseResponse[Job])
def create_job(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company),
    job_in: JobCreate,
):
    """
    Create new job.
    """
    job = crud_job.create_job(db=db, job=job_in, owner_id=current_user.id)
    return BaseResponse(object=job, message="Job created successfully")


@router.put("/{id}", response_model=BaseResponse[Job])
def update_job(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company),
    id: uuid.UUID,
    job_in: JobUpdate,
):
    """
    Update a job.
    """
    job = crud_job.get_job(db=db, id=id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    job = crud_job.update_job(db=db, db_obj=job, obj_in=job_in)
    return BaseResponse(object=job, message="Job updated successfully")


@router.delete("/{id}", response_model=BaseResponse)
def delete_job(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company),
    id: uuid.UUID,
):
    """
    Delete a job.
    """
    job = crud_job.get_job(db=db, id=id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    crud_job.remove_job(db=db, id=id)
    return BaseResponse(message="Job deleted successfully")
