"""
Notification Service
Real-time notifications and alerts
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Notification, User
from ..schemas import NotificationResponse

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        pass
    
    def create_notification(self, db: Session, user_id: str, type: str, title: str, message: str, data: Dict[str, Any] = None) -> NotificationResponse:
        """Create a new notification"""
        try:
            if data is None:
                data = {}
            
            notification = Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                data=data
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            logger.info(f"Created notification: {notification.id} for user: {user_id}")
            return NotificationResponse.model_validate(notification)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating notification: {e}")
            raise
    
    def get_notifications(self, db: Session, user_id: str, limit: int = 50) -> List[NotificationResponse]:
        """Get notifications for a user"""
        try:
            notifications = db.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(Notification.created_at.desc()).limit(limit).all()
            
            return [NotificationResponse.model_validate(notification) for notification in notifications]
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            raise
    
    def mark_as_read(self, db: Session, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if not notification:
                return False
            
            notification.is_read = True
            db.commit()
            
            logger.info(f"Marked notification as read: {notification_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking notification as read: {e}")
            raise
    
    def mark_all_as_read(self, db: Session, user_id: str) -> bool:
        """Mark all notifications as read"""
        try:
            db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).update({"is_read": True})
            
            db.commit()
            logger.info(f"Marked all notifications as read for user: {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error marking all notifications as read: {e}")
            raise
    
    def get_unread_count(self, db: Session, user_id: str) -> int:
        """Get count of unread notifications"""
        try:
            return db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).count()
            
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0
    
    def send_application_notification(self, db: Session, user_id: str, application_id: str, job_title: str) -> None:
        """Send notification about new application"""
        self.create_notification(
            db=db,
            user_id=user_id,
            type="application",
            title="New Application Received",
            message=f"You have received a new application for {job_title}",
            data={"application_id": application_id, "job_title": job_title}
        )
    
    def send_interview_notification(self, db: Session, user_id: str, interview_id: str, candidate_name: str) -> None:
        """Send notification about scheduled interview"""
        self.create_notification(
            db=db,
            user_id=user_id,
            type="interview",
            title="Interview Scheduled",
            message=f"Interview scheduled with {candidate_name}",
            data={"interview_id": interview_id, "candidate_name": candidate_name}
        )
    
    def send_fitscore_notification(self, db: Session, user_id: str, candidate_name: str, job_title: str, fit_score: float) -> None:
        """Send notification about high FitScore match"""
        self.create_notification(
            db=db,
            user_id=user_id,
            type="fitscore",
            title="High Match Found",
            message=f"{candidate_name} has a high match ({fit_score:.1%}) for {job_title}",
            data={"candidate_name": candidate_name, "job_title": job_title, "fit_score": fit_score}
        )
    
    def delete_old_notifications(self, db: Session, days_old: int = 30) -> int:
        """Delete notifications older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            deleted_count = db.query(Notification).filter(
                Notification.created_at < cutoff_date
            ).delete()
            
            db.commit()
            logger.info(f"Deleted {deleted_count} old notifications")
            return deleted_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting old notifications: {e}")
            raise