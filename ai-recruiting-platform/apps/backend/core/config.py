"""
Configuration management for AI Recruiting Platform
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Recruiting Platform"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/recruiting_platform")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_POOL_SIZE: int = 20
    
    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "https://recruiting-platform.com"])
    
    # Security
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_AT_REST_KEY", "your-encryption-key")
    WEBHOOK_HMAC_SECRET: str = os.getenv("WEBHOOK_HMAC_SECRET", "your-webhook-secret")
    IDEMPOTENCY_KEY_SALT: str = os.getenv("IDEMPOTENCY_KEY_SALT", "your-idempotency-salt")
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    HUGGINGFACE_TOKEN: Optional[str] = os.getenv("HUGGINGFACE_TOKEN")
    
    # OAuth
    GMAIL_CLIENT_ID: Optional[str] = os.getenv("GMAIL_CLIENT_ID")
    GMAIL_CLIENT_SECRET: Optional[str] = os.getenv("GMAIL_CLIENT_SECRET")
    GOOGLE_CALENDAR_CREDENTIALS_JSON: Optional[str] = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_JSON")
    
    # Storage
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "https://s3.amazonaws.com")
    S3_ACCESS_KEY_ID: Optional[str] = os.getenv("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: Optional[str] = os.getenv("S3_SECRET_ACCESS_KEY")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "resumes")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    
    # Webhooks
    ATS_WEBHOOK_SECRET: Optional[str] = os.getenv("ATS_WEBHOOK_SECRET")
    OUTREACH_WEBHOOK_SECRET: Optional[str] = os.getenv("OUTREACH_WEBHOOK_SECRET")
    CALENDAR_WEBHOOK_SECRET: Optional[str] = os.getenv("CALENDAR_WEBHOOK_SECRET")
    
    # Feature Flags
    ENABLE_SOURCING: bool = os.getenv("ENABLE_SOURCING", "true").lower() == "true"
    ENABLE_OUTREACH: bool = os.getenv("ENABLE_OUTREACH", "true").lower() == "true"
    ENABLE_SCHEDULING: bool = os.getenv("ENABLE_SCHEDULING", "true").lower() == "true"
    ENABLE_ANALYTICS: bool = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    ENABLE_HEALTH_MONITOR: bool = os.getenv("ENABLE_HEALTH_MONITOR", "true").lower() == "true"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    GRAFANA_API_KEY: Optional[str] = os.getenv("GRAFANA_API_KEY")
    PROMETHEUS_URL: Optional[str] = os.getenv("PROMETHEUS_URL")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()