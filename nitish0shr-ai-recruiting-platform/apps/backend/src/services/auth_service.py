"""
Authentication Service
JWT-based authentication with role-based access control
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt

from ..models import User
from ..schemas import UserCreate, UserResponse, UserLogin
from ..config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def register_user(self, db: Session, user: UserCreate) -> UserResponse:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user.email).first()
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Hash password
            hashed_password = self.hash_password(user.password)
            
            # Create new user
            db_user = User(
                email=user.email,
                password_hash=hashed_password,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
                organization_id=user.organization_id
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"Registered user: {db_user.email} (ID: {db_user.id})")
            return UserResponse.model_validate(db_user)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error registering user: {e}")
            raise
    
    def login_user(self, db: Session, email: str, password: str) -> Dict[str, Any]:
        """Login user and return JWT token"""
        try:
            # Find user by email
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise ValueError("Invalid email or password")
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                raise ValueError("Invalid email or password")
            
            # Check if user is active
            if not user.is_active:
                raise ValueError("User account is deactivated")
            
            # Create access token
            access_token = self.create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "role": user.role.value,
                    "organization_id": str(user.organization_id)
                }
            )
            
            logger.info(f"User logged in: {user.email} (ID: {user.id})")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserResponse.model_validate(user)
            }
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            raise
    
    def get_current_user(self, db: Session, token: str) -> User:
        """Get current user from JWT token"""
        try:
            payload = self.decode_token(token)
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token payload")
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            if not user.is_active:
                raise ValueError("User account is deactivated")
            
            return user
            
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise
    
    def update_user(self, db: Session, user_id: str, updates: Dict[str, Any]) -> Optional[UserResponse]:
        """Update user information"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Don't allow password updates through this method
            if 'password' in updates:
                del updates['password']
            
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            logger.info(f"Updated user: {user.email} (ID: {user.id})")
            return UserResponse.model_validate(user)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating user: {e}")
            raise
    
    def change_password(self, db: Session, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Verify old password
            if not self.verify_password(old_password, user.password_hash):
                raise ValueError("Invalid current password")
            
            # Update password
            user.password_hash = self.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Password changed for user: {user.email} (ID: {user.id})")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error changing password: {e}")
            raise
    
    def deactivate_user(self, db: Session, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Deactivated user: {user.email} (ID: {user.id})")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deactivating user: {e}")
            raise
    
    def has_permission(self, user: User, required_role: str) -> bool:
        """Check if user has required permission"""
        role_hierarchy = {
            'interviewer': 1,
            'recruiter': 2,
            'hiring_manager': 3,
            'admin': 4
        }
        
        user_role_level = role_hierarchy.get(user.role.value, 0)
        required_role_level = role_hierarchy.get(required_role, 0)
        
        return user_role_level >= required_role_level
    
    def is_organization_admin(self, user: User, organization_id: str) -> bool:
        """Check if user is admin of the organization"""
        return (user.role.value == 'admin' and 
                str(user.organization_id) == str(organization_id))