"""
FitScore Service
AI-powered candidate-job matching algorithm
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from openai import OpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..models import Application, Job, Candidate
from ..schemas import FitScoreResponse
from ..config import settings

logger = logging.getLogger(__name__)

class FitScoreService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def calculate_fit_score(self, db: Session, job_id: str, candidate_id: str, organization_id: str) -> FitScoreResponse:
        """Calculate comprehensive FitScore for candidate-job match"""
        try:
            # Get job and candidate
            job = db.query(Job).filter(Job.id == job_id, Job.organization_id == organization_id).first()
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id, Candidate.organization_id == organization_id).first()
            
            if not job or not candidate:
                raise ValueError("Job or candidate not found")
            
            # Calculate individual scores
            skill_match = self._calculate_skill_match(job, candidate)
            experience_match = self._calculate_experience_match(job, candidate)
            education_match = self._calculate_education_match(job, candidate)
            location_match = self._calculate_location_match(job, candidate)
            culture_fit = self._calculate_culture_fit(job, candidate)
            
            # Calculate weighted overall score
            weights = {
                'skill_match': 0.35,
                'experience_match': 0.25,
                'education_match': 0.15,
                'location_match': 0.10,
                'culture_fit': 0.15
            }
            
            overall_score = (
                skill_match * weights['skill_match'] +
                experience_match * weights['experience_match'] +
                education_match * weights['education_match'] +
                location_match * weights['location_match'] +
                culture_fit * weights['culture_fit']
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(job, candidate, {
                'skill_match': skill_match,
                'experience_match': experience_match,
                'education_match': education_match,
                'location_match': location_match,
                'culture_fit': culture_fit
            })
            
            # Update or create application with FitScore
            application = db.query(Application).filter(
                Application.job_id == job_id,
                Application.candidate_id == candidate_id
            ).first()
            
            if not application:
                application = Application(
                    job_id=job_id,
                    candidate_id=candidate_id,
                    organization_id=organization_id
                )
                db.add(application)
            
            application.fit_score = overall_score
            application.fit_score_details = {
                'skill_match': skill_match,
                'experience_match': experience_match,
                'education_match': education_match,
                'location_match': location_match,
                'culture_fit': culture_fit,
                'weights': weights,
                'calculated_at': datetime.utcnow().isoformat()
            }
            
            db.commit()
            
            return FitScoreResponse(
                application_id=str(application.id),
                job_id=job_id,
                candidate_id=candidate_id,
                overall_score=overall_score,
                skill_match=skill_match,
                experience_match=experience_match,
                education_match=education_match,
                location_match=location_match,
                culture_fit=culture_fit,
                breakdown=self._get_score_breakdown(job, candidate),
                recommendations=recommendations,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating FitScore: {e}")
            raise
    
    def _calculate_skill_match(self, job: Job, candidate: Candidate) -> float:
        """Calculate skill matching score"""
        try:
            # Get job requirements
            job_skills = []
            if job.parsed_requirements and 'required_skills' in job.parsed_requirements:
                job_skills = job.parsed_requirements['required_skills']
            elif job.requirements:
                job_skills = job.requirements
            
            # Get candidate skills
            candidate_skills = candidate.skills or []
            
            if not job_skills or not candidate_skills:
                return 0.0
            
            # Calculate skill overlap using fuzzy matching
            matched_skills = 0
            total_required_skills = len(job_skills)
            
            for job_skill in job_skills:
                job_skill_lower = job_skill.lower()
                for candidate_skill in candidate_skills:
                    candidate_skill_lower = candidate_skill.lower()
                    
                    # Exact match
                    if job_skill_lower == candidate_skill_lower:
                        matched_skills += 1
                        break
                    # Partial match
                    elif (job_skill_lower in candidate_skill_lower or 
                          candidate_skill_lower in job_skill_lower):
                        matched_skills += 0.8
                        break
            
            skill_match_score = matched_skills / total_required_skills if total_required_skills > 0 else 0
            return min(skill_match_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating skill match: {e}")
            return 0.0
    
    def _calculate_experience_match(self, job: Job, candidate: Candidate) -> float:
        """Calculate experience matching score"""
        try:
            # Get required experience from job
            required_exp = None
            if job.parsed_requirements and 'experience_required' in job.parsed_requirements:
                required_exp = job.parsed_requirements['experience_required']
            
            # Get candidate experience
            candidate_exp = candidate.experience_years
            
            if not required_exp or not candidate_exp:
                return 0.5  # Neutral score if no data
            
            # Calculate experience match
            if candidate_exp >= required_exp:
                return 1.0
            else:
                # Linear decay for less experience
                return candidate_exp / required_exp
                
        except Exception as e:
            logger.error(f"Error calculating experience match: {e}")
            return 0.5
    
    def _calculate_education_match(self, job: Job, candidate: Candidate) -> float:
        """Calculate education matching score"""
        try:
            # Get required education from job
            required_edu = None
            if job.parsed_requirements and 'education_required' in job.parsed_requirements:
                required_edu = job.parsed_requirements['education_required']
            
            # Get candidate education from parsed resume
            candidate_edu = None
            if candidate.resume_parsed and 'education' in candidate.resume_parsed:
                education_list = candidate.resume_parsed['education']
                if education_list:
                    candidate_edu = education_list[0]  # Get highest education
            
            if not required_edu or not candidate_edu:
                return 0.5  # Neutral score if no data
            
            # Simple education level matching
            education_levels = {
                'high school': 1,
                'associate': 2,
                'bachelor': 3,
                'master': 4,
                'phd': 5,
                'mba': 4
            }
            
            required_level = 0
            candidate_level = 0
            
            for level, value in education_levels.items():
                if level in required_edu.lower():
                    required_level = value
                if level in str(candidate_edu).lower():
                    candidate_level = value
            
            if candidate_level >= required_level:
                return 1.0
            else:
                return candidate_level / required_level if required_level > 0 else 0
                
        except Exception as e:
            logger.error(f"Error calculating education match: {e}")
            return 0.5
    
    def _calculate_location_match(self, job: Job, candidate: Candidate) -> float:
        """Calculate location matching score"""
        try:
            job_location = job.location
            candidate_location = candidate.location
            
            if not job_location or not candidate_location:
                return 0.5  # Neutral score if no location data
            
            job_location = job_location.lower().strip()
            candidate_location = candidate_location.lower().strip()
            
            # Exact match
            if job_location == candidate_location:
                return 1.0
            
            # Same city/state/country matching (simplified)
            if (job_location in candidate_location or 
                candidate_location in job_location):
                return 0.8
            
            # Remote work consideration
            if 'remote' in job_location or 'remote' in candidate_location:
                return 0.9
            
            # Different locations
            return 0.3
            
        except Exception as e:
            logger.error(f"Error calculating location match: {e}")
            return 0.5
    
    def _calculate_culture_fit(self, job: Job, candidate: Candidate) -> float:
        """Calculate culture fit score using AI analysis"""
        try:
            # Get job description and candidate summary
            job_desc = job.description
            candidate_summary = ""
            if candidate.resume_parsed and 'summary' in candidate.resume_parsed:
                candidate_summary = candidate.resume_parsed['summary']
            
            if not job_desc or not candidate_summary:
                return 0.5  # Neutral score if no data
            
            # Use AI to analyze culture fit
            prompt = f"""
            Analyze the culture fit between a job description and candidate profile.
            
            Job Description:
            {job_desc}
            
            Candidate Profile:
            {candidate_summary}
            
            Rate the culture fit on a scale of 0-1, where:
            0 = Poor culture fit
            0.5 = Neutral culture fit  
            1 = Excellent culture fit
            
            Consider factors like:
            - Work environment preferences
            - Communication style
            - Team collaboration
            - Company values alignment
            - Career goals alignment
            
            Return only the numeric score (0-1).
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in culture fit assessment."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            score_text = response.choices[0].message.content.strip()
            try:
                score = float(score_text)
                return max(0, min(1, score))  # Ensure score is between 0-1
            except:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating culture fit: {e}")
            return 0.5
    
    def _generate_recommendations(self, job: Job, candidate: Candidate, scores: Dict[str, float]) -> List[str]:
        """Generate personalized recommendations based on FitScore analysis"""
        recommendations = []
        
        try:
            # Skill recommendations
            if scores['skill_match'] < 0.7:
                job_skills = job.parsed_requirements.get('required_skills', []) if job.parsed_requirements else []
                candidate_skills = candidate.skills or []
                missing_skills = [skill for skill in job_skills if skill.lower() not in [cs.lower() for cs in candidate_skills]]
                
                if missing_skills:
                    recommendations.append(f"Consider developing these skills: {', '.join(missing_skills[:3])}")
            
            # Experience recommendations
            if scores['experience_match'] < 0.8:
                required_exp = job.parsed_requirements.get('experience_required', 0) if job.parsed_requirements else 0
                candidate_exp = candidate.experience_years or 0
                
                if candidate_exp < required_exp:
                    recommendations.append(f"Gain {required_exp - candidate_exp:.1f} more years of relevant experience")
            
            # Culture fit recommendations
            if scores['culture_fit'] < 0.6:
                recommendations.append("Research company culture and values to better align your application")
            
            # Positive feedback
            if scores['skill_match'] > 0.9:
                recommendations.append("Excellent skill match! Your technical skills align well with the requirements")
            
            if scores['experience_match'] > 0.9:
                recommendations.append("Strong experience match for this role")
            
            # Default recommendation if no specific ones
            if not recommendations:
                recommendations.append("Good overall match - consider applying for this position")
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Consider applying for this position"]
    
    def _get_score_breakdown(self, job: Job, candidate: Candidate) -> Dict[str, Any]:
        """Get detailed breakdown of scoring components"""
        return {
            "job_analysis": {
                "title": job.title,
                "required_skills": job.parsed_requirements.get('required_skills', []) if job.parsed_requirements else [],
                "experience_required": job.parsed_requirements.get('experience_required', 0) if job.parsed_requirements else 0
            },
            "candidate_analysis": {
                "name": f"{candidate.first_name} {candidate.last_name}",
                "skills": candidate.skills or [],
                "experience_years": candidate.experience_years,
                "current_role": candidate.current_title,
                "current_company": candidate.current_company
            }
        }
    
    def get_top_candidates(self, db: Session, job_id: str, organization_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top candidates for a job based on FitScore"""
        try:
            # Get all applications for the job
            applications = db.query(Application).filter(
                Application.job_id == job_id,
                Application.organization_id == organization_id
            ).order_by(Application.fit_score.desc()).limit(limit).all()
            
            results = []
            for app in applications:
                candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
                if candidate:
                    results.append({
                        "candidate": candidate,
                        "application": app,
                        "fit_score": app.fit_score or 0,
                        "fit_score_details": app.fit_score_details or {}
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting top candidates: {e}")
            raise