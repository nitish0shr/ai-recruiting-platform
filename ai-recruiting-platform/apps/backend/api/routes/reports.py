"""
Reports and Analytics API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from core.database import get_db, Job, Candidate, CandidateStage
from api.schemas import (
    RoleHealthRequest,
    RoleHealthResponse
)
from api.dependencies import (
    get_current_user,
    validate_job_access
)

router = APIRouter()

@router.post("/roleHealth", response_model=RoleHealthResponse)
async def get_role_health(
    request: RoleHealthRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    job: Job = Depends(validate_job_access)
):
    """Get role health metrics and recommendations"""
    try:
        from sqlalchemy import select, func, and_
        
        # Get candidate counts by stage
        stage_query = select(
            Candidate.stage,
            func.count(Candidate.id).label("count")
        ).where(
            Candidate.job_id == request.job_id,
            Candidate.organization_id == current_user.organization_id
        ).group_by(Candidate.stage)
        
        result = await db.execute(stage_query)
        stage_counts = {row.stage.value: row.count for row in result.all()}
        
        # Calculate metrics
        total_candidates = sum(stage_counts.values())
        qualified_candidates = stage_counts.get(CandidateStage.SHORTLIST.value, 0) + \
                             stage_counts.get(CandidateStage.INTERVIEW.value, 0)
        
        # Get recent activity
        new_apps_24h = await _get_recent_candidates_count(db, request.job_id, 1)
        interviews_7d = await _get_recent_interviews_count(db, request.job_id, 7)
        
        # Calculate health index
        health_index = await _calculate_health_index(
            total_candidates,
            qualified_candidates,
            new_apps_24h,
            interviews_7d
        )
        
        # Generate risks and recommendations
        risks = await _identify_risks(stage_counts, new_apps_24h, health_index)
        next_actions = await _generate_next_actions(stage_counts, risks)
        
        # Calculate reply rate (mock data)
        reply_rate = 15.3
        
        return RoleHealthResponse(
            health_index=health_index,
            qualified_on_hand=qualified_candidates,
            new_apps_24h=new_apps_24h,
            interviews_7d=interviews_7d,
            reply_rate=reply_rate,
            stage_distribution=stage_counts,
            risks=risks,
            next_actions=next_actions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get role health: {str(e)}"
        )

@router.get("/dashboard")
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard metrics and KPIs"""
    try:
        from sqlalchemy import select, func, and_
        
        # Get organization stats
        org_id = current_user.organization_id
        
        # Job counts
        job_query = select(func.count(Job.id)).where(Job.organization_id == org_id)
        total_jobs = await db.scalar(job_query)
        
        active_jobs_query = select(func.count(Job.id)).where(
            and_(Job.organization_id == org_id, Job.status == "published")
        )
        active_jobs = await db.scalar(active_jobs_query)
        
        # Candidate counts
        candidate_query = select(func.count(Candidate.id)).where(
            Candidate.organization_id == org_id
        )
        total_candidates = await db.scalar(candidate_query)
        
        # Recent candidates
        new_candidates_query = select(func.count(Candidate.id)).where(
            and_(
                Candidate.organization_id == org_id,
                Candidate.created_at >= datetime.utcnow() - timedelta(days=1)
            )
        )
        new_candidates_24h = await db.scalar(new_candidates_query)
        
        # Recent interviews (mock)
        interviews_this_week = 12
        
        # Pipeline health average (mock)
        pipeline_health_avg = 75.5
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_candidates": total_candidates,
            "new_candidates_24h": new_candidates_24h,
            "interviews_this_week": interviews_this_week,
            "pipeline_health_avg": pipeline_health_avg,
            "active_jobs_list": [  # Mock data for demo
                {
                    "id": "job_1",
                    "title": "Senior Software Engineer",
                    "candidates": 15,
                    "health": 85
                },
                {
                    "id": "job_2", 
                    "title": "Product Manager",
                    "candidates": 8,
                    "health": 72
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )

@router.get("/funnel")
async def get_funnel_analytics(
    job_id: Optional[str] = None,
    days: Optional[int] = 30,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recruitment funnel analytics"""
    try:
        from sqlalchemy import select, func, and_
        
        # Base query
        query = select(
            Candidate.stage,
            func.count(Candidate.id).label("count"),
            func.avg(Candidate.fit_score).label("avg_score")
        ).where(
            Candidate.organization_id == current_user.organization_id,
            Candidate.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        
        if job_id:
            query = query.where(Candidate.job_id == uuid.UUID(job_id))
        
        query = query.group_by(Candidate.stage)
        
        result = await db.execute(query)
        funnel_data = result.all()
        
        # Calculate conversion rates
        stages = ["new", "screening", "shortlist", "interview", "offer", "hired"]
        funnel = []
        
        for stage in stages:
            stage_data = next((row for row in funnel_data if row.stage.value == stage), None)
            if stage_data:
                funnel.append({
                    "stage": stage,
                    "count": stage_data.count,
                    "avg_score": round(float(stage_data.avg_score or 0), 2)
                })
            else:
                funnel.append({
                    "stage": stage,
                    "count": 0,
                    "avg_score": 0.0
                })
        
        # Calculate conversion rates between stages
        for i in range(1, len(funnel)):
            if funnel[i-1]["count"] > 0:
                conversion_rate = (funnel[i]["count"] / funnel[i-1]["count"]) * 100
                funnel[i]["conversion_rate"] = round(conversion_rate, 2)
            else:
                funnel[i]["conversion_rate"] = 0.0
        
        return {"funnel": funnel}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get funnel analytics: {str(e)}"
        )

# Helper functions
async def _get_recent_candidates_count(db: AsyncSession, job_id: str, days: int) -> int:
    """Get count of candidates added in recent days"""
    from sqlalchemy import select, func, and_
    
    query = select(func.count(Candidate.id)).where(
        and_(
            Candidate.job_id == uuid.UUID(job_id),
            Candidate.created_at >= datetime.utcnow() - timedelta(days=days)
        )
    )
    
    return await db.scalar(query) or 0

async def _get_recent_interviews_count(db: AsyncSession, job_id: str, days: int) -> int:
    """Get count of interviews in recent days"""
    # Mock implementation
    return 5

async def _calculate_health_index(
    total_candidates: int,
    qualified_candidates: int,
    new_apps_24h: int,
    interviews_7d: int
) -> float:
    """Calculate health index (0-100)"""
    if total_candidates == 0:
        return 0.0
    
    # Base score from qualified candidates ratio
    qualified_ratio = qualified_candidates / max(total_candidates, 1)
    base_score = qualified_ratio * 60
    
    # Bonus for recent activity
    activity_bonus = min((new_apps_24h * 2) + (interviews_7d * 3), 40)
    
    health_index = base_score + activity_bonus
    return min(100.0, health_index)

async def _identify_risks(
    stage_counts: dict,
    new_apps_24h: int,
    health_index: float
) -> List[str]:
    """Identify pipeline risks"""
    risks = []
    
    if health_index < 50:
        risks.append("Low pipeline health - consider sourcing more candidates")
    
    if new_apps_24h < 2:
        risks.append("Low application volume in last 24 hours")
    
    if stage_counts.get("new", 0) > stage_counts.get("screening", 0) * 2:
        risks.append("Backlog in screening stage")
    
    if stage_counts.get("shortlist", 0) < 3:
        risks.append("Low qualified candidate pool")
    
    return risks

async def _generate_next_actions(
    stage_counts: dict,
    risks: List[str]
) -> List[str]:
    """Generate recommended next actions"""
    actions = []
    
    if "Low pipeline health" in risks:
        actions.append("Start sourcing campaign for this role")
    
    if "Backlog in screening" in risks:
        actions.append("Review and screen pending candidates")
    
    if "Low qualified candidate pool" in risks:
        actions.append("Adjust screening criteria or expand search")
    
    actions.append("Review outreach performance and optimize")
    
    return actions