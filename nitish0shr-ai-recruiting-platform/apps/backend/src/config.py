"""
Configuration Management
Environment variables and settings
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Recruiting Platform"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ai_recruiting")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # Email Service
    EMAIL_SERVICE: str = os.getenv("EMAIL_SERVICE", "smtp")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@airecruiting.com")
    
    # File Upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/tmp/uploads")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://ai-recruiting-platform.vercel.app",
        "https://*.vercel.app"
    ]
    
    # AI Configuration
    FIT_SCORE_THRESHOLD: float = float(os.getenv("FIT_SCORE_THRESHOLD", "0.7"))
    MAX_CANDIDATES_PER_JOB: int = int(os.getenv("MAX_CANDIDATES_PER_JOB", "100"))
    
    # Demo Data
    GENERATE_DEMO_DATA: bool = os.getenv("GENERATE_DEMO_DATA", "false").lower() == "true"
    
    # Calendar Integration
    GOOGLE_CALENDAR_ENABLED: bool = os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() == "true"
    OUTLOOK_CALENDAR_ENABLED: bool = os.getenv("OUTLOOK_CALENDAR_ENABLED", "false").lower() == "true"
    
    # Webhook URLs
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "webhook-secret")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()