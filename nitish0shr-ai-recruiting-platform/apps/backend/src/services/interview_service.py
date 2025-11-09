"""
Interview Service
Interview scheduling, conducting, and management
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from openai import OpenAI

from ..models import Interview, Application, Candidate, User
from ..schemas import InterviewCreate, InterviewResponse
from ..config import settings

logger = logging.getLogger(__name__)

class InterviewService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def schedule_interview(self, db: Session, interview: InterviewCreate, organization_id: str) -> InterviewResponse:
        """Schedule a new interview"""
        try:
            # Validate that application exists and belongs to organization
            application = db.query(Application).filter(
                Application.id == interview.application_id,
                Application.organization_id == organization_id
            ).first()
            
            if not application:
                raise ValueError("Application not found or does not belong to organization")
            
            # Check for scheduling conflicts
            conflicts = self._check_scheduling_conflicts(
                db, interview.interviewer_id, interview.scheduled_at, interview.duration_minutes
            )
            
            if conflicts:
                raise ValueError("Scheduling conflict detected")
            
            # Generate meeting link if needed
            meeting_link = interview.meeting_link
            if not meeting_link and interview.type == 'video':
                meeting_link = self._generate_meeting_link()
            
            db_interview = Interview(
                application_id=interview.application_id,
                candidate_id=interview.candidate_id,
                interviewer_id=interview.interviewer_id,
                scheduled_at=interview.scheduled_at,
                duration_minutes=interview.duration_minutes,
                type=interview.type,
                meeting_link=meeting_link,
                notes=interview.notes
            )
            
            db.add(db_interview)
            db.commit()
            db.refresh(db_interview)
            
            logger.info(f"Scheduled interview: {db_interview.id}")
            return InterviewResponse.model_validate(db_interview)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error scheduling interview: {e}")
            raise
    
    def _check_scheduling_conflicts(self, db: Session, interviewer_id: str, scheduled_at: datetime, duration_minutes: int) -> bool:
        """Check for scheduling conflicts"""
        try:
            end_time = scheduled_at + timedelta(minutes=duration_minutes)
            
            conflicts = db.query(Interview).filter(
                Interview.interviewer_id == interviewer_id,
                Interview.scheduled_at < end_time,
                Interview.scheduled_at > scheduled_at - timedelta(minutes=duration_minutes)
            ).count()
            
            return conflicts > 0
            
        except Exception as e:
            logger.error(f"Error checking scheduling conflicts: {e}")
            return False
    
    def _generate_meeting_link(self) -> str:
        """Generate meeting link (placeholder implementation)"""
        # In production, integrate with Zoom, Google Meet, or other video conferencing APIs
        return f"https://meet.example.com/interview/{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def get_upcoming_interviews(self, db: Session, organization_id: str, days_ahead: int = 7) -> List[InterviewResponse]:
        """Get upcoming interviews for organization"""
        try:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=days_ahead)
            
            interviews = db.query(Interview).join(Application).filter(
                Application.organization_id == organization_id,
                Interview.scheduled_at >= start_date,
                Interview.scheduled_at <= end_date
            ).order_by(Interview.scheduled_at).all()
            
            return [InterviewResponse.model_validate(interview) for interview in interviews]
            
        except Exception as e:
            logger.error(f"Error getting upcoming interviews: {e}")
            raise
    
    def conduct_interview(self, db: Session, interview_id: str, organization_id: str) -> Dict[str, Any]:
        """Conduct interview with AI assistance"""
        try:
            interview = db.query(Interview).join(Application).filter(
                Interview.id == interview_id,
                Application.organization_id == organization_id
            ).first()
            
            if not interview:
                raise ValueError("Interview not found")
            
            # Generate AI-powered interview questions
            questions = self._generate_interview_questions(interview)
            
            # Update interview status
            interview.status = 'in_progress'
            interview.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "interview_id": interview_id,
                "questions": questions,
                "meeting_link": interview.meeting_link,
                "status": interview.status
            }
            
        except Exception as e:
            logger.error(f"Error conducting interview: {e}")
            raise
    
    def _generate_interview_questions(self, interview: Interview) -> List[Dict[str, Any]]:
        """Generate AI-powered interview questions"""
        try:
            # Get job and candidate information
            application = interview.application
            job = application.job
            candidate = interview.candidate
            
            prompt = f"""
            Generate a set of interview questions for a job interview.
            
            Job Details:
            Title: {job.title}
            Requirements: {job.parsed_requirements.get('required_skills', []) if job.parsed_requirements else []}
            
            Candidate Details:
            Name: {candidate.first_name} {candidate.last_name}
            Experience: {candidate.experience_years} years
            Skills: {candidate.skills[:5] if candidate.skills else []}
            
            Generate 8-10 interview questions including:
            1. Technical questions relevant to the job
            2. Behavioral questions
            3. Questions about candidate's experience
            4. Questions to assess culture fit
            5. Questions about career goals
            
            Return in JSON format:
            {{
                "questions": [
                    {{
                        "type": "technical|behavioral|experience|culture|goals",
                        "question": "question text",
                        "follow_up": "suggested follow-up question"
                    }}
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert interviewer creating thoughtful interview questions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = eval(response.choices[0].message.content)
            return content.get('questions', [])
            
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            # Fallback questions
            return [
                {"type": "experience", "question": "Tell me about your relevant experience.", "follow_up": "Can you give a specific example?"},
                {"type": "technical", "question": "What technical skills do you bring to this role?", "follow_up": "How have you applied these skills?"}
            ]
    
    def complete_interview(self, db: Session, interview_id: str, feedback: Dict[str, Any], rating: float) -> InterviewResponse:
        """Complete interview and save feedback"""
        try:
            interview = db.query(Interview).filter(Interview.id == interview_id).first()
            if not interview:
                raise ValueError("Interview not found")
            
            interview.status = 'completed'
            interview.feedback = feedback
            interview.rating = rating
            interview.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(interview)
            
            logger.info(f"Completed interview: {interview_id}")
            return InterviewResponse.model_validate(interview)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error completing interview: {e}")
            raise
    
    def get_interview_analytics(self, db: Session, organization_id: str) -> Dict[str, Any]:
        """Get interview analytics for organization"""
        try:
            # Get interview statistics
            total_interviews = db.query(Interview).join(Application).filter(
                Application.organization_id == organization_id
            ).count()
            
            completed_interviews = db.query(Interview).join(Application).filter(
                Application.organization_id == organization_id,
                Interview.status == 'completed'
            ).count()
            
            scheduled_interviews = db.query(Interview).join(Application).filter(
                Application.organization_id == organization_id,
                Interview.status == 'scheduled'
            ).count()
            
            avg_rating = db.query(Interview).join(Application).filter(
                Application.organization_id == organization_id,
                Interview.rating.isnot(None)
            ).all()
            
            if avg_rating:
                avg_rating_score = sum(i.rating for i in avg_rating if i.rating) / len(avg_rating)
            else:
                avg_rating_score = 0
            
            return {
                "total_interviews": total_interviews,
                "completed_interviews": completed_interviews,
                "scheduled_interviews": scheduled_interviews,
                "completion_rate": (completed_interviews / total_interviews * 100) if total_interviews > 0 else 0,
                "average_rating": round(avg_rating_score, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting interview analytics: {e}")
            raise