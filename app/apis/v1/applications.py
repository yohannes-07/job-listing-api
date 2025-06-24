from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.apis.deps import get_db, get_current_applicant, get_current_company
from app.crud import application as crud_application, job as crud_job
from app.schemas.application import (
    Application,
    ApplicationCreate,
    ApplicationForCompany,
    ApplicationStatusUpdate,
)
from app.schemas.base import BaseResponse
from app.db.models import User
import cloudinary.uploader
import uuid
from fastapi_pagination import Page, paginate

router = APIRouter()


@router.get("/", response_model=Page[ApplicationForCompany])
def read_job_applications(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company),
):
    """
    Retrieve applications for a specific job.
    """
    job = crud_job.get_job(db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    applications_query = crud_application.get_applications_by_job_id_query(
        db, job_id=job_id
    )
    return paginate(applications_query)


@router.put("/{application_id}", response_model=BaseResponse[Application])
def update_application_status(
    application_id: uuid.UUID,
    status_in: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company),
):
    """
    Update an application's status.
    """
    application = crud_application.get_application(db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.job.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    application = crud_application.update_application_status(
        db, db_obj=application, status=status_in.status
    )
    return BaseResponse(object=application, message="Application status updated successfully")


@router.post("/", response_model=BaseResponse[Application])
def apply_for_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_applicant),
    resume: UploadFile = File(...),
    cover_letter: str = Form(None, max_length=2000),
):
    """
    Apply for a job.
    """
    # Check if job exists
    job = crud_job.get_job(db, id=job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check for duplicate application
    existing_application = crud_application.get_application_by_applicant_and_job(
        db, applicant_id=current_user.id, job_id=job_id
    )
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job",
        )

    # Validate resume file type
    if resume.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF resumes are accepted",
        )

    # Upload resume to Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(resume.file, resource_type="raw")
        resume_link = upload_result["secure_url"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {e}",
        )

    application_data = ApplicationCreate(job_id=job_id, cover_letter=cover_letter)

    # Create application
    application = crud_application.create_application(
        db,
        application=application_data,
        applicant_id=current_user.id,
        resume_link=resume_link,
    )

    return BaseResponse(
        object=application, message="Application submitted successfully"
    )
