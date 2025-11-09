"""
Email Service
Automated outreach and campaign management
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from openai import OpenAI

from ..models import Campaign, Email, Candidate, Job
from ..schemas import CampaignCreate, CampaignResponse
from ..config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def create_campaign(self, db: Session, campaign: CampaignCreate, organization_id: str) -> CampaignResponse:
        """Create a new email campaign"""
        try:
            db_campaign = Campaign(
                name=campaign.name,
                job_id=campaign.job_id,
                template_id=campaign.template_id,
                target_criteria=campaign.target_criteria,
                organization_id=organization_id
            )
            
            db.add(db_campaign)
            db.commit()
            db.refresh(db_campaign)
            
            logger.info(f"Created campaign: {db_campaign.name} (ID: {db_campaign.id})")
            return CampaignResponse.model_validate(db_campaign)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating campaign: {e}")
            raise
    
    def launch_campaign(self, db: Session, campaign_id: str, organization_id: str) -> bool:
        """Launch email campaign to target candidates"""
        try:
            campaign = db.query(Campaign).filter(
                Campaign.id == campaign_id,
                Campaign.organization_id == organization_id
            ).first()
            
            if not campaign:
                raise ValueError("Campaign not found")
            
            # Get target candidates based on criteria
            target_candidates = self._get_target_candidates(db, campaign.target_criteria, organization_id)
            
            # Generate personalized emails
            for candidate in target_candidates:
                email_content = self._generate_personalized_email(campaign, candidate)
                
                email = Email(
                    campaign_id=campaign_id,
                    candidate_id=candidate.id,
                    recipient_email=candidate.email,
                    subject=email_content['subject'],
                    content=email_content['content']
                )
                
                db.add(email)
            
            campaign.status = 'active'
            campaign.sent_count = len(target_candidates)
            campaign.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Launched campaign: {campaign.name} to {len(target_candidates)} candidates")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error launching campaign: {e}")
            raise
    
    def _get_target_candidates(self, db: Session, criteria: Dict[str, Any], organization_id: str) -> List[Candidate]:
        """Get target candidates based on campaign criteria"""
        try:
            from ..models import Candidate
            
            query = db.query(Candidate).filter(Candidate.organization_id == organization_id)
            
            # Filter by skills
            if 'skills' in criteria:
                for skill in criteria['skills']:
                    query = query.filter(Candidate.skills.ilike(f"%{skill}%"))
            
            # Filter by experience
            if 'min_experience' in criteria:
                query = query.filter(Candidate.experience_years >= criteria['min_experience'])
            
            # Filter by location
            if 'location' in criteria:
                query = query.filter(Candidate.location.ilike(f"%{criteria['location']}%"))
            
            # Filter by current company
            if 'current_company' in criteria:
                query = query.filter(Candidate.current_company.ilike(f"%{criteria['current_company']}%"))
            
            return query.limit(100).all()  # Limit to 100 candidates per campaign
            
        except Exception as e:
            logger.error(f"Error getting target candidates: {e}")
            return []
    
    def _generate_personalized_email(self, campaign: Campaign, candidate: Candidate) -> Dict[str, str]:
        """Generate personalized email content using AI"""
        try:
            job = db.query(Job).filter(Job.id == campaign.job_id).first()
            
            prompt = f"""
            Generate a personalized outreach email for a job opportunity.
            
            Job Details:
            Title: {job.title}
            Company: {job.organization.name if hasattr(job, 'organization') else 'Our Company'}
            
            Candidate Details:
            Name: {candidate.first_name} {candidate.last_name}
            Current Role: {candidate.current_title or 'Professional'}
            Skills: {', '.join(candidate.skills[:5]) if candidate.skills else 'Various'}
            
            Generate:
            1. A compelling subject line
            2. Personalized email content that:
                - Addresses the candidate by name
                - Mentions relevant skills/experience
                - Highlights why this opportunity is a good fit
                - Includes a clear call-to-action
                - Is professional but engaging
                - Is concise (150-200 words)
            
            Return in JSON format:
            {{
                "subject": "email subject line",
                "content": "email body content"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert recruiter writing personalized outreach emails."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = eval(response.choices[0].message.content)
            return content
            
        except Exception as e:
            logger.error(f"Error generating personalized email: {e}")
            # Fallback to template
            return {
                "subject": f"Exciting Opportunity: {job.title}",
                "content": f"Hi {candidate.first_name},\n\nI hope this email finds you well. We have an exciting opportunity that matches your background...\n\nBest regards,\nRecruitment Team"
            }
    
    def get_campaigns(self, db: Session, organization_id: str) -> List[CampaignResponse]:
        """Get all campaigns for an organization"""
        try:
            campaigns = db.query(Campaign).filter(
                Campaign.organization_id == organization_id
            ).all()
            
            return [CampaignResponse.model_validate(campaign) for campaign in campaigns]
            
        except Exception as e:
            logger.error(f"Error getting campaigns: {e}")
            raise
    
    def get_campaign_analytics(self, db: Session, campaign_id: str, organization_id: str) -> Dict[str, Any]:
        """Get campaign analytics and performance metrics"""
        try:
            campaign = db.query(Campaign).filter(
                Campaign.id == campaign_id,
                Campaign.organization_id == organization_id
            ).first()
            
            if not campaign:
                raise ValueError("Campaign not found")
            
            # Calculate metrics
            open_rate = (campaign.opened_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0
            click_rate = (campaign.clicked_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0
            reply_rate = (campaign.replied_count / campaign.sent_count * 100) if campaign.sent_count > 0 else 0
            
            return {
                "campaign_id": campaign_id,
                "campaign_name": campaign.name,
                "status": campaign.status,
                "sent_count": campaign.sent_count,
                "opened_count": campaign.opened_count,
                "clicked_count": campaign.clicked_count,
                "replied_count": campaign.replied_count,
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "reply_rate": round(reply_rate, 2),
                "created_at": campaign.created_at,
                "updated_at": campaign.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign analytics: {e}")
            raise