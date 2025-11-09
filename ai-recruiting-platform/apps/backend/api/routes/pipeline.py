"""
Pipeline API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from core.database import get_db, Candidate, CandidateStage, ActivityLog
from api.schemas import (
    PipelineMoveRequest,
    PipelineMoveResponse
)
from api.dependencies import (
    get_current_user,
    validate_candidate_access,
    log_activity
)

router = APIRouter()

@router.post("/move", response_model=PipelineMoveResponse)
async def move_candidate_stage(
    request: PipelineMoveRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Move candidate to different pipeline stage"""
    try:
        # Get candidate with validation
        from sqlalchemy import select
        candidate_query = select(Candidate).where(Candidate.id == request.candidate_id)
        result = await db.execute(candidate_query)
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        # Validate organization access
        if candidate.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update stage
        old_stage = candidate.stage
        candidate.stage = request.to_stage
        
        await db.commit()
        await db.refresh(candidate)
        
        # Log activity
        activity = await log_activity(
            db,
            candidate.organization_id,
            current_user.id,
            "candidate",
            candidate.id,
            "stage_changed",
            {
                "from_stage": old_stage.value,
                "to_stage": request.to_stage.value,
                "notes": request.notes
            }
        )
        
        return PipelineMoveResponse(
            candidate=candidate,
            activity_id=activity.id if activity else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to move candidate: {str(e)}"
        )

@router.get("/stages")
async def get_pipeline_stages(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available pipeline stages"""
    stages = [
        {"value": stage.value, "label": stage.value.replace("_", " ").title()}
        for stage in CandidateStage
    ]
    
    return {"stages": stages}

@router.get("/analytics")
async def get_pipeline_analytics(
    job_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get pipeline analytics and metrics"""
    try:
        from sqlalchemy import select, func, and_
        
        # Base query
        query = select(
            Candidate.stage,
            func.count(Candidate.id).label("count")
        ).where(Candidate.organization_id == current_user.organization_id)
        
        if job_id:
            query = query.where(Candidate.job_id == uuid.UUID(job_id))
        
        query = query.group_by(Candidate.stage)
        
        result = await db.execute(query)
        stage_counts = result.all()
        
        # Format response
        analytics = {
            "total_candidates": sum(row.count for row in stage_counts),
            "stage_distribution": {
                row.stage.value: row.count for row in stage_counts
            },
            "conversion_rates": {}
        }
        
        # Calculate conversion rates
        total = analytics["total_candidates"]
        if total > 0:
            for row in stage_counts:
                analytics["conversion_rates"][row.stage.value] = {
                    "count": row.count,
                    "percentage": round((row.count / total) * 100, 2)
                }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )