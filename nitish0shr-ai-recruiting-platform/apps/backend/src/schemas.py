"""
Pydantic Schemas for API Validation and Response
Complete schema definitions for all API endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEWER = "interviewer"

class ApplicationStatus(str, Enum):
    NEW = "new"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"

class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

# Base Schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.RECRUITER
    organization_id: str

class UserResponse(BaseSchema):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    organization_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Job Schemas
class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    requirements: Optional[List[str]] = []
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: Optional[str] = None

class JobResponse(BaseSchema):
    id: str
    title: str
    description: str
    requirements: List[str]
    parsed_requirements: Optional[Dict[str, Any]] = {}
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    status: str
    organization_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

# Candidate Schemas
class CandidateCreate(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume_text: Optional[str] = None
    skills: Optional[List[str]] = []
    experience_years: Optional[float] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    location: Optional[str] = None

class CandidateUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    location: Optional[str] = None

class CandidateResponse(BaseSchema):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume_text: Optional[str] = None
    resume_parsed: Optional[Dict[str, Any]] = {}
    skills: List[str] = []
    experience_years: Optional[float] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    location: Optional[str] = None
    organization_id: str
    created_at: datetime
    updated_at: datetime

# Application Schemas
class ApplicationCreate(BaseModel):
    job_id: str
    candidate_id: str
    source: Optional[str] = "direct"
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None

class ApplicationResponse(BaseSchema):
    id: str
    job_id: str
    candidate_id: str
    organization_id: str
    status: ApplicationStatus
    fit_score: Optional[float] = None
    fit_score_details: Optional[Dict[str, Any]] = {}
    source: str
    notes: Optional[str] = None
    applied_at: datetime
    created_at: datetime
    updated_at: datetime
    job: Optional[JobResponse] = None
    candidate: Optional[CandidateResponse] = None

# FitScore Schemas
class FitScoreResponse(BaseSchema):
    application_id: str
    job_id: str
    candidate_id: str
    overall_score: float
    skill_match: float
    experience_match: float
    education_match: float
    location_match: float
    culture_fit: float
    breakdown: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime

# Interview Schemas
class InterviewCreate(BaseModel):
    application_id: str
    candidate_id: str
    interviewer_id: str
    scheduled_at: datetime
    duration_minutes: Optional[int] = 60
    type: Optional[str] = "video"
    meeting_link: Optional[str] = None
    notes: Optional[str] = None

class InterviewUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[InterviewStatus] = None
    notes: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = None
    rating: Optional[float] = None

class InterviewResponse(BaseSchema):
    id: str
    application_id: str
    candidate_id: str
    interviewer_id: str
    scheduled_at: datetime
    duration_minutes: int
    type: str
    status: InterviewStatus
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    feedback: Optional[Dict[str, Any]] = {}
    rating: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    candidate: Optional[CandidateResponse] = None
    interviewer: Optional[UserResponse] = None

# Campaign Schemas
class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    job_id: str
    template_id: str
    target_criteria: Optional[Dict[str, Any]] = {}

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[CampaignStatus] = None
    target_criteria: Optional[Dict[str, Any]] = None

class CampaignResponse(BaseSchema):
    id: str
    name: str
    job_id: str
    template_id: str
    status: CampaignStatus
    target_criteria: Dict[str, Any] = {}
    sent_count: int
    opened_count: int
    clicked_count: int
    replied_count: int
    created_by: str
    created_at: datetime
    updated_at: datetime

# Analytics Schemas
class AnalyticsResponse(BaseSchema):
    total_jobs: int
    active_jobs: int
    total_candidates: int
    total_applications: int
    applications_by_status: Dict[str, int]
    average_fit_score: float
    time_to_hire_avg: Optional[float] = None
    conversion_rates: Dict[str, float]
    top_skills: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]

class DetailedAnalyticsResponse(BaseSchema):
    date_range: Dict[str, str]
    metrics: Dict[str, Any]
    trends: Dict[str, List[Dict[str, Any]]]
    demographics: Dict[str, Any]
    performance: Dict[str, Any]

# Notification Schemas
class NotificationResponse(BaseSchema):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    data: Dict[str, Any] = {}
    is_read: bool
    created_at: datetime

# Email Schemas
class EmailTemplateCreate(BaseModel):
    name: str
    subject: str
    content: str
    type: str
    variables: Optional[List[str]] = []

class EmailTemplateResponse(BaseSchema):
    id: str
    name: str
    subject: str
    content: str
    type: str
    variables: List[str]
    created_at: datetime
    updated_at: datetime

# Assessment Schemas
class AssessmentCreate(BaseModel):
    application_id: str
    type: str
    questions: List[Dict[str, Any]]

class AssessmentResponse(BaseSchema):
    id: str
    application_id: str
    type: str
    questions: List[Dict[str, Any]]
    responses: Dict[str, Any] = {}
    score: Optional[float] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

# Search Schemas
class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = {}
    limit: Optional[int] = 20
    offset: Optional[int] = 0

class SearchResponse(BaseSchema):
    results: List[Dict[str, Any]]
    total: int
    query: str
    filters: Dict[str, Any]

# Webhook Schemas
class WebhookPayload(BaseModel):
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime

# Config Schemas
class ConfigUpdate(BaseModel):
    key: str
    value: Any

class ConfigResponse(BaseSchema):
    key: str
    value: Any
    updated_at: datetime

# Error Schemas
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)