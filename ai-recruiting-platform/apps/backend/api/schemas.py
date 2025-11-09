"""
API schemas and response models
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import UUID

from core.database import JobStatus, CandidateStage, CandidateSource, OutreachStatus

# Base schemas
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None

class Error(BaseModel):
    """Error response model"""
    code: str
    message: str
    correlation_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Job schemas
class JobCreateRequest(BaseModel):
    """Job creation request"""
    jd_text: Optional[str] = Field(None, description="Job description text")
    file_url: Optional[str] = Field(None, description="URL to JD document")
    title: Optional[str] = Field(None, description="Job title")
    location: Optional[str] = Field(None, description="Job location")
    compensation: Optional[Dict[str, Any]] = Field(None, description="Compensation range")
    
    @validator('jd_text', 'file_url')
    def check_content_provided(cls, v, values):
        if not v and not values.get('jd_text') and not values.get('file_url'):
            raise ValueError('Either jd_text or file_url must be provided')
        return v

class JobResponse(BaseModel):
    """Job response model"""
    id: UUID
    title: str
    description: str
    requirements: List[str] = []
    must_haves: List[str] = []
    nice_to_haves: List[str] = []
    location: Optional[str] = None
    min_years: Optional[int] = None
    max_years: Optional[int] = None
    compensation_min: Optional[float] = None
    compensation_max: Optional[float] = None
    compensation_currency: str = "USD"
    status: JobStatus
    public_url: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobPublishResponse(BaseModel):
    """Job publish response"""
    public_url: str
    external_id: Optional[str] = None

# Candidate schemas
class CandidateIngestRequest(BaseModel):
    """Candidate ingestion request"""
    job_id: UUID
    file_url: Optional[str] = None
    email_parse: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None

class CandidateResponse(BaseModel):
    """Candidate response model"""
    id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    current_role: Optional[str] = None
    current_company: Optional[str] = None
    years_experience: Optional[int] = None
    skills: List[str] = []
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    resume_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    stackoverflow_url: Optional[str] = None
    source: CandidateSource
    stage: CandidateStage
    job_id: UUID
    fit_score: Optional[float] = None
    coverage: Optional[float] = None
    is_duplicate: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CandidateScoreResponse(BaseModel):
    """Candidate score response"""
    fit_score: float
    coverage: float
    red_flags: List[Dict[str, Any]] = []
    factors: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []

# Pipeline schemas
class PipelineMoveRequest(BaseModel):
    """Pipeline move request"""
    candidate_id: UUID
    to_stage: CandidateStage
    notes: Optional[str] = None

class PipelineMoveResponse(BaseModel):
    """Pipeline move response"""
    candidate: CandidateResponse
    activity_id: UUID

# Outreach schemas
class OutreachSendRequest(BaseModel):
    """Outreach send request"""
    candidate_id: UUID
    template_id: UUID
    step: Optional[int] = 1
    personalization: Optional[Dict[str, Any]] = None

class OutreachSendResponse(BaseModel):
    """Outreach send response"""
    message_id: str
    status: str

# Scheduling schemas
class ScheduleProposeRequest(BaseModel):
    """Schedule proposal request"""
    candidate_id: UUID
    recruiter_id: UUID
    duration: Optional[int] = 45
    availability: Optional[List[Dict[str, Any]]] = None

class TimeSlot(BaseModel):
    """Time slot model"""
    id: str
    start: datetime
    end: datetime
    timezone: str

class ScheduleProposeResponse(BaseModel):
    """Schedule proposal response"""
    slots: List[TimeSlot]

class ScheduleConfirmRequest(BaseModel):
    """Schedule confirmation request"""
    candidate_id: UUID
    slot_id: str

class ScheduleConfirmResponse(BaseModel):
    """Schedule confirmation response"""
    event_id: str
    meeting_link: Optional[str] = None

# Report schemas
class RoleHealthRequest(BaseModel):
    """Role health request"""
    job_id: UUID

class RoleHealthResponse(BaseModel):
    """Role health response"""
    health_index: float
    qualified_on_hand: int
    new_apps_24h: int
    interviews_7d: int
    reply_rate: float
    stage_distribution: Dict[str, int]
    risks: List[str] = []
    next_actions: List[str] = []

# Preparation schemas
class PrepPackRequest(BaseModel):
    """Prep pack request"""
    candidate_id: UUID

class PrepPackResponse(BaseModel):
    """Prep pack response"""
    pdf_url: str
    content: Dict[str, Any]

# Webhook schemas
class WebhookEvent(BaseModel):
    """Webhook event model"""
    type: str
    timestamp: datetime
    data: Dict[str, Any]
    signature: Optional[str] = None

# Dashboard schemas
class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_jobs: int
    active_jobs: int
    total_candidates: int
    new_candidates_24h: int
    interviews_this_week: int
    pipeline_health_avg: float

class PipelineStage(BaseModel):
    """Pipeline stage model"""
    stage: CandidateStage
    count: int
    candidates: List[CandidateResponse] = []

# Search schemas
class SearchRequest(BaseModel):
    """Search request"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class SearchResponse(BaseModel):
    """Search response"""
    results: List[Dict[str, Any]]
    total: int
    query: str

# Analytics schemas
class AnalyticsRequest(BaseModel):
    """Analytics request"""
    metrics: List[str]
    date_range: Dict[str, datetime]
    group_by: Optional[str] = None

class AnalyticsResponse(BaseModel):
    """Analytics response"""
    data: Dict[str, Any]
    summary: Dict[str, Any]

# Settings schemas
class OrganizationSettings(BaseModel):
    """Organization settings"""
    name: str
    domain: str
    settings: Dict[str, Any]

class UserSettings(BaseModel):
    """User settings"""
    name: str
    email: str
    role: str
    preferences: Dict[str, Any] = {}

# File upload schemas
class FileUploadResponse(BaseModel):
    """File upload response"""
    file_id: str
    url: str
    filename: str
    content_type: str
    size: int