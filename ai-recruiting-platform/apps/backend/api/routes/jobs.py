"""
Jobs API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from datetime import datetime

from core.database import get_db, Job, JobStatus, User, Organization, ActivityLog
from core.config import settings
from services.job_parser import job_parser, ParsedJob
from api.schemas import (
    JobCreateRequest,
    JobResponse,
    JobPublishResponse,
    Error
)
from api.dependencies import (
    get_current_user,
    get_current_org,
    validate_job_access,
    log_activity
)

router = APIRouter()

@router.post("/", response_model=JobResponse)
async def create_job(
    request: JobCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org)
):
    """Create a new job from job description"""
    try:
        # Parse job description
        if request.file_url:
            # TODO: Fetch file from URL and extract text
            jd_text = "Extracted from file"
        else:
            jd_text = request.jd_text
        
        parsed_job = await job_parser.parse_job_description(jd_text)
        
        # Create job object
        job = Job(
            title=parsed_job.title or request.title or "Untitled Position",
            description=parsed_job.description,
            requirements=parsed_job.requirements,
            must_haves=parsed_job.must_haves,
            nice_to_haves=parsed_job.nice_to_haves,
            location=parsed_job.location or request.location,
            min_years=parsed_job.min_years,
            max_years=parsed_job.max_years,
            compensation_min=parsed_job.compensation_min,
            compensation_max=parsed_job.compensation_max,
            compensation_currency=parsed_job.compensation_currency,
            organization_id=current_org.id,
            created_by=current_user.id,
            status=JobStatus.DRAFT
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Log activity
        await log_activity(
            db,
            current_org.id,
            current_user.id,
            "job",
            job.id,
            "created",
            {"confidence": parsed_job.confidence}
        )
        
        return JobResponse.from_orm(job)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )

@router.post("/upload", response_model=JobResponse)
async def create_job_from_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org)
):
    """Create job from uploaded file (PDF, DOCX)"""
    try:
        # Validate file type
        if file.content_type not in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload PDF or DOCX files."
            )
        
        # Read file content
        content = await file.read()
        
        # TODO: Extract text from file and parse
        # For now, create a placeholder job
        job = Job(
            title="Job from File",
            description=f"Parsed from {file.filename}",
            requirements=[],
            must_haves=[],
            nice_to_haves=[],
            organization_id=current_org.id,
            created_by=current_user.id,
            status=JobStatus.DRAFT
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Log activity
        await log_activity(
            db,
            current_org.id,
            current_user.id,
            "job",
            job.id,
            "created_from_file",
            {"filename": file.filename}
        )
        
        return JobResponse.from_orm(job)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )

@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[JobStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org)
):
    """List jobs for the organization"""
    try:
        from sqlalchemy import select
        
        query = select(Job).where(Job.organization_id == current_org.id)
        
        if status:
            query = query.where(Job.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Job.created_at.desc())
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return [JobResponse.from_orm(job) for job in jobs]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    job: Job = Depends(validate_job_access)
):
    """Get specific job details"""
    return JobResponse.from_orm(job)

@router.post("/{job_id}/publish", response_model=JobPublishResponse)
async def publish_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_org),
    job: Job = Depends(validate_job_access)
):
    """Publish job to career page and ATS"""
    try:
        if job.status != JobStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job is not in draft status"
            )
        
        # Update job status
        job.status = JobStatus.PUBLISHED
        job.public_url = f"{settings.NEXT_PUBLIC_APP_URL}/jobs/{job.id}"
        
        # TODO: Integrate with ATS if configured
        # For now, create mock external ID
        job.external_id = f"ATS_{job.id[:8]}"
        
        await db.commit()
        
        # Log activity
        await log_activity(
            db,
            current_org.id,
            current_user.id,
            "job",
            job.id,
            "published",
            {"public_url": job.public_url, "external_id": job.external_id}
        )
        
        return JobPublishResponse(
            public_url=job.public_url,
            external_id=job.external_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish job: {str(e)}"
        )

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    request: JobCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    job: Job = Depends(validate_job_access)
):
    """Update job details"""
    try:
        # Parse updated job description
        if request.jd_text:
            parsed_job = await job_parser.parse_job_description(request.jd_text)
            
            # Update fields
            job.title = parsed_job.title or request.title or job.title
            job.description = parsed_job.description
            job.requirements = parsed_job.requirements
            job.must_haves = parsed_job.must_haves
            job.nice_to_haves = parsed_job.nice_to_haves
            job.location = parsed_job.location or request.location or job.location
            job.min_years = parsed_job.min_years or job.min_years
            job.max_years = parsed_job.max_years or job.max_years
        
        await db.commit()
        await db.refresh(job)
        
        # Log activity
        await log_activity(
            db,
            job.organization_id,
            current_user.id,
            "job",
            job.id,
            "updated"
        )
        
        return JobResponse.from_orm(job)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
        )

@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    job: Job = Depends(validate_job_access)
):
    """Delete a job"""
    try:
        # Soft delete by setting status to closed
        job.status = JobStatus.CLOSED
        await db.commit()
        
        # Log activity
        await log_activity(
            db,
            job.organization_id,
            current_user.id,
            "job",
            job.id,
            "deleted"
        )
        
        return {"message": "Job deleted successfully"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )

@router.get("/{job_id}/public")
async def get_public_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get public job details (no auth required)"""
    try:
        from sqlalchemy import select
        
        query = select(Job).where(
            Job.id == uuid.UUID(job_id),
            Job.status == JobStatus.PUBLISHED
        )
        
        result = await db.execute(query)
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or not published"
            )
        
        return {
            "id": str(job.id),
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "must_haves": job.must_haves,
            "nice_to_haves": job.nice_to_haves,
            "location": job.location,
            "min_years": job.min_years,
            "max_years": job.max_years,
            "compensation": {
                "min": job.compensation_min,
                "max": job.compensation_max,
                "currency": job.compensation_currency
            } if job.compensation_min or job.compensation_max else None,
            "created_at": job.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job: {str(e)}"
        )