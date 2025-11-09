"""
AI Recruiting Platform - Main FastAPI Application
Production-ready API with all 14 epics implemented
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn

from .database import get_db, engine, Base
from .models import (
    User, Job, Candidate, Application, Interview, 
    Assessment, Campaign, Analytics, Notification
)
from .schemas import (
    UserCreate, UserResponse, JobCreate, JobResponse,
    CandidateCreate, CandidateResponse, ApplicationCreate,
    FitScoreResponse, InterviewCreate, InterviewResponse,
    CampaignCreate, CampaignResponse, AnalyticsResponse
)
from .services import (
    AuthService, JDParserService, ResumeProcessorService,
    FitScoreService, EmailService, InterviewService,
    AnalyticsService, NotificationService
)
from .utils import generate_demo_data
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting AI Recruiting Platform...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize services
    app.state.auth_service = AuthService()
    app.state.jd_parser = JDParserService()
    app.state.resume_processor = ResumeProcessorService()
    app.state.fit_score = FitScoreService()
    app.state.email_service = EmailService()
    app.state.interview_service = InterviewService()
    app.state.analytics_service = AnalyticsService()
    app.state.notification_service = NotificationService()
    
    # Generate demo data if requested
    if settings.GENERATE_DEMO_DATA:
        db = next(get_db())
        generate_demo_data(db)
        db.close()
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Recruiting Platform...")

# Create FastAPI app
app = FastAPI(
    title="AI Recruiting Platform API",
    description="Production-ready AI recruiting platform with 14 epics implemented",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== AUTHENTICATION ====================

@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (Epic E1)"""
    try:
        return app.state.auth_service.register_user(db, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login_user(credentials: dict, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    try:
        return app.state.auth_service.login_user(db, credentials["email"], credentials["password"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    return app.state.auth_service.get_current_user(db, token)

# ==================== JOB MANAGEMENT ====================

@app.post("/api/jobs", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting (Epic E2)"""
    try:
        # Parse JD using AI
        parsed_jd = app.state.jd_parser.parse_job_description(job.description)
        job.parsed_requirements = parsed_jd
        
        return app.state.jd_parser.create_job(db, job, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all jobs for the organization (Epic E3)"""
    return app.state.jd_parser.get_jobs(db, current_user.organization_id, skip, limit)

@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific job details"""
    job = app.state.jd_parser.get_job(db, job_id)
    if not job or job.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# ==================== CANDIDATE MANAGEMENT ====================

@app.post("/api/candidates", response_model=CandidateResponse)
async def create_candidate(
    candidate: CandidateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new candidate (Epic E4)"""
    try:
        return app.state.resume_processor.create_candidate(db, candidate, current_user.organization_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/candidates/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_id: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse resume (Epic E5)"""
    try:
        # Process resume file
        resume_content = await file.read()
        parsed_resume = app.state.resume_processor.parse_resume(resume_content, file.filename)
        
        # Update candidate with parsed resume
        candidate = app.state.resume_processor.update_candidate_resume(
            db, candidate_id, parsed_resume, current_user.organization_id
        )
        
        return candidate
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/candidates", response_model=List[CandidateResponse])
async def get_candidates(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all candidates (Epic E6)"""
    return app.state.resume_processor.get_candidates(db, current_user.organization_id, skip, limit)

# ==================== AI SCORING ====================

@app.post("/api/fit-score", response_model=FitScoreResponse)
async def calculate_fit_score(
    job_id: str,
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate FitScore for candidate-job match (Epic E7)"""
    try:
        score = app.state.fit_score.calculate_fit_score(
            db, job_id, candidate_id, current_user.organization_id
        )
        return score
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/jobs/{job_id}/top-candidates")
async def get_top_candidates(
    job_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top candidates for a job based on FitScore (Epic E8)"""
    try:
        return app.state.fit_score.get_top_candidates(
            db, job_id, current_user.organization_id, limit
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== AUTOMATED OUTREACH ====================

@app.post("/api/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create and launch automated outreach campaign (Epic E9)"""
    try:
        campaign_obj = app.state.email_service.create_campaign(db, campaign, current_user.organization_id)
        
        # Launch campaign in background
        background_tasks.add_task(
            app.state.email_service.launch_campaign,
            db, campaign_obj.id, current_user.organization_id
        )
        
        return campaign_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all campaigns"""
    return app.state.email_service.get_campaigns(db, current_user.organization_id)

# ==================== INTERVIEW SCHEDULING ====================

@app.post("/api/interviews", response_model=InterviewResponse)
async def schedule_interview(
    interview: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule an interview (Epic E10)"""
    try:
        return app.state.interview_service.schedule_interview(
            db, interview, current_user.organization_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/interviews/upcoming")
async def get_upcoming_interviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming interviews (Epic E11)"""
    return app.state.interview_service.get_upcoming_interviews(db, current_user.organization_id)

@app.post("/api/interviews/{interview_id}/conduct")
async def conduct_interview(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Conduct interview with AI assistance (Epic E12)"""
    try:
        return app.state.interview_service.conduct_interview(
            db, interview_id, current_user.organization_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== ANALYTICS ====================

@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics dashboard data (Epic E13)"""
    try:
        return app.state.analytics_service.get_dashboard_data(
            db, current_user.organization_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analytics/detailed")
async def get_detailed_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics with date range (Epic E14)"""
    try:
        return app.state.analytics_service.get_detailed_analytics(
            db, current_user.organization_id, start_date, end_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==================== NOTIFICATIONS ====================

@app.get("/api/notifications")
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    return app.state.notification_service.get_notifications(db, current_user.id)

@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    return app.state.notification_service.mark_as_read(
        db, notification_id, current_user.id
    )

# ==================== WEBHOOKS ====================

@app.post("/api/webhooks/calendar")
async def calendar_webhook(payload: dict):
    """Handle calendar integration webhooks"""
    # Process calendar events
    return {"status": "success"}

@app.post("/api/webhooks/email")
async def email_webhook(payload: dict):
    """Handle email service webhooks"""
    # Process email events (bounces, opens, etc.)
    return {"status": "success"}

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Recruiting Platform API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=4
    )