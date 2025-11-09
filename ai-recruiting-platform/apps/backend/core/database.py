"""
Database configuration and models for AI Recruiting Platform
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
import enum
from typing import Optional, List, Dict, Any
from datetime import datetime

from .config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Enums
class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"

class CandidateStage(str, enum.Enum):
    NEW = "new"
    SCREENING = "screening"
    SHORTLIST = "shortlist"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"

class CandidateSource(str, enum.Enum):
    LINKEDIN = "linkedin"
    GITHUB = "github"
    STACKOVERFLOW = "stackoverflow"
    UPLOAD = "upload"
    EMAIL = "email"
    REFERRAL = "referral"

class OutreachStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"

class RedFlagType(str, enum.Enum):
    SHORT_TENURE = "short_tenure"
    COMP_MISMATCH = "comp_mismatch"
    VISA_BLOCK = "visa_block"
    FREQUENT_HOPS = "frequent_hops"

# Database Models
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    settings = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="recruiter")
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(ARRAY(String), default=list)
    must_haves = Column(ARRAY(String), default=list)
    nice_to_haves = Column(ARRAY(String), default=list)
    location = Column(String(255))
    min_years = Column(Integer)
    max_years = Column(Integer)
    compensation_min = Column(Float)
    compensation_max = Column(Float)
    compensation_currency = Column(String(3), default="USD")
    status = Column(Enum(JobStatus), default=JobStatus.DRAFT)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    public_url = Column(String(500))
    external_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index("idx_jobs_org_status", "organization_id", "status"),
        Index("idx_jobs_created_at", "created_at"),
    )

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50))
    location = Column(String(255))
    current_role = Column(String(255))
    current_company = Column(String(255))
    years_experience = Column(Integer)
    skills = Column(ARRAY(String), default=list)
    education = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    resume_url = Column(String(500))
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    stackoverflow_url = Column(String(500))
    source = Column(Enum(CandidateSource), nullable=False)
    stage = Column(Enum(CandidateStage), default=CandidateStage.NEW)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    fit_score = Column(Float)
    coverage = Column(Float)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index("idx_candidates_job_stage", "job_id", "stage"),
        Index("idx_candidates_org_email", "organization_id", "email"),
        Index("idx_candidates_fit_score", "fit_score"),
    )

class CandidateScore(Base):
    __tablename__ = "candidate_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False, unique=True)
    fit_score = Column(Float, nullable=False)
    coverage = Column(Float, nullable=False)
    factors = Column(JSON, default=list)
    red_flags = Column(JSON, default=list)
    evidence = Column(JSON, default=list)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Index
    __table_args__ = (
        Index("idx_scores_candidate", "candidate_id"),
    )

class OutreachSequence(Base):
    __tablename__ = "outreach_sequences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    template = Column(Text, nullable=False)
    subject = Column(String(500), nullable=False)
    step = Column(Integer, nullable=False)
    delay_days = Column(Integer, default=0)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class OutreachMessage(Base):
    __tablename__ = "outreach_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    sequence_id = Column(UUID(as_uuid=True), ForeignKey("outreach_sequences.id"), nullable=False)
    status = Column(Enum(OutreachStatus), default=OutreachStatus.PENDING)
    sent_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    replied_at = Column(DateTime(timezone=True))
    message_id = Column(String(255), unique=True)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index("idx_outreach_candidate", "candidate_id"),
        Index("idx_outreach_status", "status"),
    )

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    interviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=45)
    meeting_link = Column(String(500))
    calendar_event_id = Column(String(255))
    prep_pack_url = Column(String(500))
    status = Column(String(50), default="scheduled")
    feedback = Column(JSON)
    rating = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index("idx_activity_org", "organization_id"),
        Index("idx_activity_entity", "entity_type", "entity_id"),
        Index("idx_activity_created", "created_at"),
    )

class PipelineHealth(Base):
    __tablename__ = "pipeline_health"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, unique=True)
    health_index = Column(Float, nullable=False)
    qualified_on_hand = Column(Integer, nullable=False)
    new_apps_24h = Column(Integer, default=0)
    interviews_7d = Column(Integer, default=0)
    reply_rate = Column(Float, default=0.0)
    stage_distribution = Column(JSON, default=dict)
    risks = Column(ARRAY(String), default=list)
    next_actions = Column(ARRAY(String), default=list)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Index
    __table_args__ = (
        Index("idx_health_job", "job_id"),
    )

# Database dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()