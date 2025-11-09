"""
Analytics Service
Comprehensive analytics and reporting
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models import Job, Candidate, Application, Interview, Analytics
from ..schemas import AnalyticsResponse, DetailedAnalyticsResponse
from ..config import settings

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        pass
    
    def get_dashboard_data(self, db: Session, organization_id: str) -> AnalyticsResponse:
        """Get dashboard analytics data"""
        try:
            # Basic counts
            total_jobs = db.query(Job).filter(Job.organization_id == organization_id).count()
            active_jobs = db.query(Job).filter(
                Job.organization_id == organization_id,
                Job.status == 'open'
            ).count()
            total_candidates = db.query(Candidate).filter(Candidate.organization_id == organization_id).count()
            total_applications = db.query(Application).filter(Application.organization_id == organization_id).count()
            
            # Applications by status
            applications_by_status = {}
            status_counts = db.query(Application.status, func.count(Application.id)).filter(
                Application.organization_id == organization_id
            ).group_by(Application.status).all()
            
            for status, count in status_counts:
                applications_by_status[status] = count
            
            # Average FitScore
            avg_fit_score = db.query(func.avg(Application.fit_score)).filter(
                Application.organization_id == organization_id,
                Application.fit_score.isnot(None)
            ).scalar() or 0
            
            # Time to hire (average)
            time_to_hire = self._calculate_time_to_hire(db, organization_id)
            
            # Conversion rates
            conversion_rates = self._calculate_conversion_rates(db, organization_id)
            
            # Top skills
            top_skills = self._get_top_skills(db, organization_id)
            
            # Recent activity
            recent_activity = self._get_recent_activity(db, organization_id)
            
            return AnalyticsResponse(
                total_jobs=total_jobs,
                active_jobs=active_jobs,
                total_candidates=total_candidates,
                total_applications=total_applications,
                applications_by_status=applications_by_status,
                average_fit_score=round(avg_fit_score, 2),
                time_to_hire_avg=time_to_hire,
                conversion_rates=conversion_rates,
                top_skills=top_skills,
                recent_activity=recent_activity
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise
    
    def get_detailed_analytics(self, db: Session, organization_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> DetailedAnalyticsResponse:
        """Get detailed analytics with date range"""
        try:
            if not start_date:
                start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
            if not end_date:
                end_date = datetime.utcnow().isoformat()
            
            # Parse dates
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Trends data
            trends = self._get_trends_data(db, organization_id, start_dt, end_dt)
            
            # Demographics
            demographics = self._get_demographics_data(db, organization_id)
            
            # Performance metrics
            performance = self._get_performance_metrics(db, organization_id, start_dt, end_dt)
            
            return DetailedAnalyticsResponse(
                date_range={"start": start_date, "end": end_date},
                metrics=self.get_dashboard_data(db, organization_id).dict(),
                trends=trends,
                demographics=demographics,
                performance=performance
            )
            
        except Exception as e:
            logger.error(f"Error getting detailed analytics: {e}")
            raise
    
    def _calculate_time_to_hire(self, db: Session, organization_id: str) -> Optional[float]:
        """Calculate average time to hire"""
        try:
            # Get hired applications
            hired_apps = db.query(Application).filter(
                Application.organization_id == organization_id,
                Application.status == 'hired'
            ).all()
            
            if not hired_apps:
                return None
            
            total_days = 0
            count = 0
            
            for app in hired_apps:
                if app.created_at and app.updated_at:
                    days_diff = (app.updated_at - app.created_at).days
                    if 0 < days_diff < 365:  # Reasonable range
                        total_days += days_diff
                        count += 1
            
            return total_days / count if count > 0 else None
            
        except Exception as e:
            logger.error(f"Error calculating time to hire: {e}")
            return None
    
    def _calculate_conversion_rates(self, db: Session, organization_id: str) -> Dict[str, float]:
        """Calculate conversion rates at each stage"""
        try:
            total_applications = db.query(Application).filter(
                Application.organization_id == organization_id
            ).count()
            
            if total_applications == 0:
                return {}
            
            # Applications by status
            status_counts = db.query(Application.status, func.count(Application.id)).filter(
                Application.organization_id == organization_id
            ).group_by(Application.status).all()
            
            conversion_rates = {}
            for status, count in status_counts:
                conversion_rates[status] = round(count / total_applications * 100, 2)
            
            return conversion_rates
            
        except Exception as e:
            logger.error(f"Error calculating conversion rates: {e}")
            return {}
    
    def _get_top_skills(self, db: Session, organization_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top skills from candidates and job requirements"""
        try:
            # Get skills from candidates
            candidates = db.query(Candidate).filter(
                Candidate.organization_id == organization_id
            ).all()
            
            skill_counts = {}
            for candidate in candidates:
                if candidate.skills:
                    for skill in candidate.skills:
                        skill_lower = skill.lower()
                        skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
            
            # Get skills from job requirements
            jobs = db.query(Job).filter(Job.organization_id == organization_id).all()
            
            job_skill_counts = {}
            for job in jobs:
                if job.parsed_requirements and 'required_skills' in job.parsed_requirements:
                    for skill in job.parsed_requirements['required_skills']:
                        skill_lower = skill.lower()
                        job_skill_counts[skill_lower] = job_skill_counts.get(skill_lower, 0) + 1
            
            # Combine and sort
            combined_skills = {}
            for skill, count in skill_counts.items():
                combined_skills[skill] = combined_skills.get(skill, 0) + count
            
            for skill, count in job_skill_counts.items():
                combined_skills[skill] = combined_skills.get(skill, 0) + count
            
            # Sort by count and return top skills
            sorted_skills = sorted(combined_skills.items(), key=lambda x: x[1], reverse=True)
            
            return [
                {"skill": skill, "count": count}
                for skill, count in sorted_skills[:limit]
            ]
            
        except Exception as e:
            logger.error(f"Error getting top skills: {e}")
            return []
    
    def _get_recent_activity(self, db: Session, organization_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity across the platform"""
        try:
            activities = []
            
            # Recent applications
            recent_apps = db.query(Application).filter(
                Application.organization_id == organization_id
            ).order_by(Application.created_at.desc()).limit(limit//2).all()
            
            for app in recent_apps:
                activities.append({
                    "type": "application",
                    "description": f"New application for {app.job.title}",
                    "timestamp": app.created_at,
                    "details": {
                        "candidate_name": f"{app.candidate.first_name} {app.candidate.last_name}",
                        "status": app.status
                    }
                })
            
            # Recent interviews
            recent_interviews = db.query(Interview).join(Application).filter(
                Application.organization_id == organization_id
            ).order_by(Interview.created_at.desc()).limit(limit//2).all()
            
            for interview in recent_interviews:
                activities.append({
                    "type": "interview",
                    "description": f"Interview scheduled for {interview.application.job.title}",
                    "timestamp": interview.created_at,
                    "details": {
                        "candidate_name": f"{interview.candidate.first_name} {interview.candidate.last_name}",
                        "interviewer_name": f"{interview.interviewer.first_name} {interview.interviewer.last_name}",
                        "scheduled_at": interview.scheduled_at
                    }
                })
            
            # Sort by timestamp and return
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    def _get_trends_data(self, db: Session, organization_id: str, start_date: datetime, end_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """Get trends data over time period"""
        try:
            trends = {
                "applications": [],
                "interviews": [],
                "hires": []
            }
            
            # Daily application trends
            current_date = start_date
            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)
                
                app_count = db.query(Application).filter(
                    Application.organization_id == organization_id,
                    Application.created_at >= current_date,
                    Application.created_at < next_date
                ).count()
                
                trends["applications"].append({
                    "date": current_date.isoformat(),
                    "count": app_count
                })
                
                current_date = next_date
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting trends data: {e}")
            return {}
    
    def _get_demographics_data(self, db: Session, organization_id: str) -> Dict[str, Any]:
        """Get demographics data"""
        try:
            # Experience distribution
            candidates = db.query(Candidate).filter(
                Candidate.organization_id == organization_id
            ).all()
            
            experience_ranges = {
                "0-2 years": 0,
                "3-5 years": 0,
                "6-10 years": 0,
                "11+ years": 0
            }
            
            for candidate in candidates:
                exp = candidate.experience_years or 0
                if exp <= 2:
                    experience_ranges["0-2 years"] += 1
                elif exp <= 5:
                    experience_ranges["3-5 years"] += 1
                elif exp <= 10:
                    experience_ranges["6-10 years"] += 1
                else:
                    experience_ranges["11+ years"] += 1
            
            return {
                "experience_distribution": experience_ranges,
                "total_candidates": len(candidates)
            }
            
        except Exception as e:
            logger.error(f"Error getting demographics data: {e}")
            return {}
    
    def _get_performance_metrics(self, db: Session, organization_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            # Application processing time
            applications = db.query(Application).filter(
                Application.organization_id == organization_id,
                Application.created_at >= start_date,
                Application.created_at <= end_date
            ).all()
            
            if applications:
                avg_processing_time = sum(
                    (app.updated_at - app.created_at).days 
                    for app in applications 
                    if app.updated_at and app.created_at
                ) / len(applications)
            else:
                avg_processing_time = 0
            
            return {
                "average_processing_time_days": round(avg_processing_time, 1),
                "total_applications_period": len(applications)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}