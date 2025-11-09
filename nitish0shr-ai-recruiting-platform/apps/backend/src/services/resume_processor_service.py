"""
Resume Processor Service
AI-powered resume parsing and candidate management
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from openai import OpenAI
import PyPDF2
import io

from ..models import Candidate, Application
from ..schemas import CandidateCreate, CandidateResponse, ApplicationResponse
from ..config import settings

logger = logging.getLogger(__name__)

class ResumeProcessorService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def parse_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Parse resume file and extract structured information"""
        try:
            # Extract text from file
            if filename.lower().endswith('.pdf'):
                text = self._extract_text_from_pdf(file_content)
            elif filename.lower().endswith(('.txt', '.text')):
                text = file_content.decode('utf-8')
            elif filename.lower().endswith('.docx'):
                # For simplicity, we'll use a basic approach for DOCX
                # In production, use python-docx library
                text = file_content.decode('utf-8', errors='ignore')
            else:
                text = file_content.decode('utf-8', errors='ignore')
            
            # Use AI to parse the extracted text
            return self._parse_resume_text(text)
            
        except Exception as e:
            logger.error(f"Error parsing resume file: {e}")
            return self._fallback_parse(file_content.decode('utf-8', errors='ignore'))
    
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def _parse_resume_text(self, text: str) -> Dict[str, Any]:
        """Use AI to parse resume text"""
        try:
            prompt = f"""
            Parse the following resume and extract structured information:
            
            Resume Text:
            {text}
            
            Extract the following information in JSON format:
            - personal_info: name, email, phone, location
            - summary: professional summary or objective
            - experience: list of work experiences with company, title, duration, description
            - education: list of educational qualifications
            - skills: technical skills, soft skills, languages
            - certifications: professional certifications
            - achievements: notable achievements and awards
            - experience_years: total years of experience
            - current_company: current or most recent company
            - current_title: current or most recent job title
            """
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert resume parser. Extract information accurately and structure it properly."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            parsed_data = eval(response.choices[0].message.content)
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing resume text: {e}")
            return self._fallback_parse(text)
    
    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """Fallback parsing using regex patterns"""
        parsed = {
            "personal_info": {},
            "summary": None,
            "experience": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "achievements": [],
            "experience_years": None,
            "current_company": None,
            "current_title": None
        }
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            parsed["personal_info"]["email"] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b', text)
        if phone_match:
            parsed["personal_info"]["phone"] = phone_match.group(0)
        
        # Extract skills (common tech skills)
        skill_patterns = [
            r'\b(?:Python|Java|JavaScript|React|Node\.js|SQL|NoSQL|AWS|Azure|Docker|Kubernetes|Git|Linux|Windows)\b',
            r'\b(?:Leadership|Communication|Teamwork|Problem-solving|Analytical|Project Management|Agile|Scrum)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            parsed["skills"].extend(matches)
        
        parsed["skills"] = list(set(parsed["skills"]))  # Remove duplicates
        
        # Extract experience years
        exp_patterns = [
            r'(\d+)\s*(?:\+|years?)\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?',
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    years = int(matches[0])
                    parsed["experience_years"] = years
                    break
                except:
                    pass
        
        return parsed
    
    def create_candidate(self, db: Session, candidate: CandidateCreate, organization_id: str) -> CandidateResponse:
        """Create a new candidate"""
        try:
            db_candidate = Candidate(
                email=candidate.email,
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                phone=candidate.phone,
                linkedin_url=candidate.linkedin_url,
                resume_text=candidate.resume_text,
                skills=candidate.skills,
                experience_years=candidate.experience_years,
                current_company=candidate.current_company,
                current_title=candidate.current_title,
                location=candidate.location,
                organization_id=organization_id
            )
            
            db.add(db_candidate)
            db.commit()
            db.refresh(db_candidate)
            
            logger.info(f"Created candidate: {db_candidate.email} (ID: {db_candidate.id})")
            return CandidateResponse.model_validate(db_candidate)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating candidate: {e}")
            raise
    
    def update_candidate_resume(self, db: Session, candidate_id: str, parsed_resume: Dict[str, Any], organization_id: str) -> CandidateResponse:
        """Update candidate with parsed resume information"""
        try:
            candidate = db.query(Candidate).filter(
                Candidate.id == candidate_id,
                Candidate.organization_id == organization_id
            ).first()
            
            if not candidate:
                raise ValueError("Candidate not found")
            
            # Update candidate with parsed information
            candidate.resume_parsed = parsed_resume
            
            # Extract and update specific fields
            personal_info = parsed_resume.get("personal_info", {})
            if "email" in personal_info and personal_info["email"] != candidate.email:
                candidate.email = personal_info["email"]
            
            skills = parsed_resume.get("skills", [])
            if skills:
                candidate.skills = skills
            
            experience_years = parsed_resume.get("experience_years")
            if experience_years:
                candidate.experience_years = experience_years
            
            current_company = parsed_resume.get("current_company")
            if current_company:
                candidate.current_company = current_company
            
            current_title = parsed_resume.get("current_title")
            if current_title:
                candidate.current_title = current_title
            
            candidate.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(candidate)
            
            logger.info(f"Updated candidate resume: {candidate.id}")
            return CandidateResponse.model_validate(candidate)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating candidate resume: {e}")
            raise
    
    def get_candidates(self, db: Session, organization_id: str, skip: int = 0, limit: int = 100) -> List[CandidateResponse]:
        """Get all candidates for an organization"""
        try:
            candidates = db.query(Candidate).filter(
                Candidate.organization_id == organization_id
            ).offset(skip).limit(limit).all()
            
            return [CandidateResponse.model_validate(candidate) for candidate in candidates]
            
        except Exception as e:
            logger.error(f"Error getting candidates: {e}")
            raise
    
    def search_candidates(self, db: Session, organization_id: str, query: str, skills: List[str] = None, limit: int = 20) -> List[CandidateResponse]:
        """Search candidates by skills, experience, etc."""
        try:
            candidates_query = db.query(Candidate).filter(
                Candidate.organization_id == organization_id
            )
            
            if query:
                search_term = f"%{query}%"
                candidates_query = candidates_query.filter(
                    (Candidate.first_name.ilike(search_term) |
                     Candidate.last_name.ilike(search_term) |
                     Candidate.current_company.ilike(search_term) |
                     Candidate.current_title.ilike(search_term))
                )
            
            if skills:
                # Simple skill matching - in production, use more sophisticated matching
                for skill in skills:
                    candidates_query = candidates_query.filter(
                        Candidate.skills.ilike(f"%{skill}%")
                    )
            
            candidates = candidates_query.limit(limit).all()
            return [CandidateResponse.model_validate(candidate) for candidate in candidates]
            
        except Exception as e:
            logger.error(f"Error searching candidates: {e}")
            raise
    
    def create_application(self, db: Session, job_id: str, candidate_id: str, organization_id: str) -> ApplicationResponse:
        """Create a new application"""
        try:
            # Check if application already exists
            existing_app = db.query(Application).filter(
                Application.job_id == job_id,
                Application.candidate_id == candidate_id
            ).first()
            
            if existing_app:
                return ApplicationResponse.model_validate(existing_app)
            
            application = Application(
                job_id=job_id,
                candidate_id=candidate_id,
                organization_id=organization_id
            )
            
            db.add(application)
            db.commit()
            db.refresh(application)
            
            logger.info(f"Created application: {application.id}")
            return ApplicationResponse.model_validate(application)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating application: {e}")
            raise
    
    def get_applications(self, db: Session, organization_id: str, job_id: str = None, status: str = None, skip: int = 0, limit: int = 100) -> List[ApplicationResponse]:
        """Get applications with optional filtering"""
        try:
            applications_query = db.query(Application).filter(
                Application.organization_id == organization_id
            )
            
            if job_id:
                applications_query = applications_query.filter(Application.job_id == job_id)
            
            if status:
                applications_query = applications_query.filter(Application.status == status)
            
            applications = applications_query.offset(skip).limit(limit).all()
            
            return [ApplicationResponse.model_validate(app) for app in applications]
            
        except Exception as e:
            logger.error(f"Error getting applications: {e}")
            raise