"""
Outreach API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db, Candidate, OutreachMessage, OutreachStatus
from api.schemas import (
    OutreachSendRequest,
    OutreachSendResponse
)
from api.dependencies import (
    get_current_user,
    validate_candidate_access,
    log_activity
)

router = APIRouter()

@router.post("/send", response_model=OutreachSendResponse)
async def send_outreach(
    request: OutreachSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send outreach message to candidate"""
    try:
        # Get candidate
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
        
        # Create outreach message (mock implementation)
        outreach_message = OutreachMessage(
            candidate_id=candidate.id,
            sequence_id=request.template_id,
            status=OutreachStatus.SENT,
            message_id=f"msg_{uuid.uuid4()}"
        )
        
        db.add(outreach_message)
        await db.commit()
        
        # Log activity
        await log_activity(
            db,
            candidate.organization_id,
            current_user.id,
            "candidate",
            candidate.id,
            "outreach_sent",
            {
                "template_id": str(request.template_id),
                "step": request.step
            }
        )
        
        return OutreachSendResponse(
            message_id=outreach_message.message_id,
            status=outreach_message.status.value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send outreach: {str(e)}"
        )

@router.get("/templates")
async def get_outreach_templates(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get available outreach templates"""
    # Mock templates for demo
    templates = [
        {
            "id": "template_1",
            "name": "Initial Outreach",
            "subject": "Exciting opportunity at {{company}}",
            "content": "Hi {{name}}, I found your profile and think you'd be perfect for our {{role}} position...",
            "variables": ["name", "company", "role"]
        },
        {
            "id": "template_2",
            "name": "Follow-up",
            "subject": "Following up on {{role}} opportunity",
            "content": "Hi {{name}}, just wanted to follow up on my previous message about the {{role}} position...",
            "variables": ["name", "role"]
        }
    ]
    
    return {"templates": templates}

@router.get("/sequences")
async def get_outreach_sequences(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get outreach sequences with metrics"""
    # Mock data for demo
    sequences = [
        {
            "id": "seq_1",
            "name": "Engineering Outreach",
            "steps": 3,
            "open_rate": 45.2,
            "reply_rate": 12.8,
            "active": True
        },
        {
            "id": "seq_2",
            "name": "Executive Outreach",
            "steps": 2,
            "open_rate": 38.5,
            "reply_rate": 8.3,
            "active": True
        }
    ]
    
    return {"sequences": sequences}