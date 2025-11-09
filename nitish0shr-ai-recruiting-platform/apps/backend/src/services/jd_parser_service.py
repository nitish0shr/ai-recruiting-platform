"""
Job Description Parser Service
AI-powered job description parsing and analysis
"""

import re
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
import spacy

from ..models import Job
from ..schemas import JobCreate, JobResponse
from ..config import settings

logger = logging.getLogger(__name__)

class JDParserService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found, using basic parsing")
            self.nlp = None
    
    def parse_job_description(self, description: str) -> Dict[str, Any]:
        """Parse job description using AI to extract structured information"""
        try:
            # Use OpenAI to parse JD
            prompt = f"""
            Parse the following job description and extract structured information:
            
            Job Description:
            {description}
            
            Extract the following information in JSON format:
            - required_skills: list of required technical and soft skills
            - preferred_skills: list of preferred/nice-to-have skills
            - experience_required: minimum years of experience (if mentioned)
            - education_required: educational requirements
            - responsibilities: key job responsibilities
            - benefits: job benefits and perks
            - work_environment: work environment details
            - salary_range: salary information (if mentioned)
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst. Parse job descriptions accurately."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            parsed_data = eval(response.choices[0].message.content)
            
            # Extract additional info using regex/spaCy
            if self.nlp:
                doc = self.nlp(description)
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                parsed_data["entities"] = entities
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing job description: {e}")
            return self._fallback_parse(description)
    
    def _fallback_parse(self, description: str) -> Dict[str, Any]:
        """Fallback parsing using regex patterns"""
        parsed = {
            "required_skills": [],
            "preferred_skills": [],
            "experience_required": None,
            "education_required": None,
            "responsibilities": [],
            "benefits": [],
            "work_environment": None,
            "salary_range": None
        }
        
        # Extract skills (basic pattern matching)
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|React|Node\.js|SQL|NoSQL|AWS|Azure|Docker|Kubernetes)\b',
            r'\b(?:Leadership|Communication|Teamwork|Problem-solving|Analytical)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            parsed["required_skills"].extend(matches)
        
        # Extract experience
        exp_match = re.search(r'(\d+)\s*(?:\+|years?)\s*(?:of\s*)?experience', description, re.IGNORECASE)
        if exp_match:
            parsed["experience_required"] = int(exp_match.group(1))
        
        # Extract education
        edu_match = re.search(r'\b(?:Bachelor|Master|PhD|BS|MS|MBA)\b.*?(?:degree|in)', description, re.IGNORECASE)
        if edu_match:
            parsed["education_required"] = edu_match.group(0)
        
        return parsed
    
    def create_job(self, db: Session, job: JobCreate, user_id: str) -> JobResponse:
        """Create a new job posting"""
        try:
            # Get organization_id from user
            from ..models import User
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            db_job = Job(
                title=job.title,
                description=job.description,
                requirements=job.requirements,
                parsed_requirements=job.parsed_requirements if hasattr(job, 'parsed_requirements') else {},
                department=job.department,
                location=job.location,
                employment_type=job.employment_type,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                organization_id=user.organization_id,
                created_by=user_id
            )
            
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
            
            logger.info(f"Created job: {db_job.title} (ID: {db_job.id})")
            return JobResponse.model_validate(db_job)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating job: {e}")
            raise
    
    def get_jobs(self, db: Session, organization_id: str, skip: int = 0, limit: int = 100) -> List[JobResponse]:
        """Get all jobs for an organization"""
        try:
            jobs = db.query(Job).filter(
                Job.organization_id == organization_id
            ).offset(skip).limit(limit).all()
            
            return [JobResponse.model_validate(job) for job in jobs]
            
        except Exception as e:
            logger.error(f"Error getting jobs: {e}")
            raise
    
    def get_job(self, db: Session, job_id: str) -> Optional[JobResponse]:
        """Get specific job by ID"""
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                return JobResponse.model_validate(job)
            return None
            
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {e}")
            raise
    
    def update_job(self, db: Session, job_id: str, updates: Dict[str, Any]) -> Optional[JobResponse]:
        """Update job details"""
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return None
            
            for key, value in updates.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            job.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(job)
            
            logger.info(f"Updated job: {job.title} (ID: {job.id})")
            return JobResponse.model_validate(job)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating job {job_id}: {e}")
            raise
    
    def delete_job(self, db: Session, job_id: str) -> bool:
        """Delete a job posting"""
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return False
            
            db.delete(job)
            db.commit()
            
            logger.info(f"Deleted job: {job_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting job {job_id}: {e}")
            raise
    
    def search_jobs(self, db: Session, organization_id: str, query: str, limit: int = 10) -> List[JobResponse]:
        """Search jobs using full-text search"""
        try:
            # Simple search implementation - in production, use PostgreSQL full-text search
            search_term = f"%{query}%"
            jobs = db.query(Job).filter(
                Job.organization_id == organization_id,
                (Job.title.ilike(search_term) |
                 Job.description.ilike(search_term) |
                 Job.department.ilike(search_term))
            ).limit(limit).all()
            
            return [JobResponse.model_validate(job) for job in jobs]
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            raise