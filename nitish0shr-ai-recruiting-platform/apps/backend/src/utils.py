"""
Utility Functions
Demo data generation and helper functions
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from .models import (
    Organization, User, Job, Candidate, Application, 
    Interview, Campaign, Analytics, Notification
)
from .schemas import UserRole, ApplicationStatus, InterviewStatus, CampaignStatus

def generate_demo_data(db: Session) -> None:
    """Generate comprehensive demo data for testing"""
    print("Generating demo data...")
    
    # Create organization
    org = Organization(
        id=uuid.UUID("12345678-1234-1234-1234-123456789012"),
        name="TechCorp Industries",
        domain="techcorp.com",
        settings={
            "features": {
                "ai_parsing": True,
                "fit_score": True,
                "automated_outreach": True,
                "interview_scheduling": True
            }
        }
    )
    db.add(org)
    db.commit()
    
    # Create admin user
    admin = User(
        id=uuid.UUID("12345678-1234-1234-1234-123456789013"),
        email="admin@techcorp.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/J9eHCOOLm",  # password: admin123
        first_name="John",
        last_name="Admin",
        role=UserRole.ADMIN,
        organization_id=org.id,
        is_active=True
    )
    db.add(admin)
    
    # Create recruiter user
    recruiter = User(
        id=uuid.UUID("12345678-1234-1234-1234-123456789014"),
        email="recruiter@techcorp.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/J9eHCOOLm",  # password: recruiter123
        first_name="Sarah",
        last_name="Recruiter",
        role=UserRole.RECRUITER,
        organization_id=org.id,
        is_active=True
    )
    db.add(recruiter)
    
    # Create demo jobs
    jobs_data = [
        {
            "title": "Senior Software Engineer",
            "description": "We are looking for a Senior Software Engineer to join our team. You will be responsible for designing, developing, and maintaining our core platform. The ideal candidate has 5+ years of experience with Python, React, and cloud technologies.",
            "requirements": ["Python", "React", "AWS", "Docker", "PostgreSQL", "Leadership"],
            "department": "Engineering",
            "location": "San Francisco, CA",
            "employment_type": "Full-time",
            "salary_min": 120000,
            "salary_max": 180000
        },
        {
            "title": "Product Manager",
            "description": "Seeking an experienced Product Manager to drive our product strategy. You will work with cross-functional teams to define product vision, roadmap, and execute on key initiatives.",
            "requirements": ["Product Strategy", "Roadmap Planning", "Agile", "Data Analysis", "Communication"],
            "department": "Product",
            "location": "New York, NY",
            "employment_type": "Full-time",
            "salary_min": 100000,
            "salary_max": 150000
        },
        {
            "title": "Data Scientist",
            "description": "Join our data science team to build machine learning models and derive insights from complex datasets. Strong background in statistics, Python, and ML frameworks required.",
            "requirements": ["Python", "Machine Learning", "Statistics", "SQL", "TensorFlow", "R"],
            "department": "Data Science",
            "location": "Remote",
            "employment_type": "Full-time",
            "salary_min": 110000,
            "salary_max": 160000
        }
    ]
    
    jobs = []
    for i, job_data in enumerate(jobs_data):
        job = Job(
            id=uuid.UUID(f"12345678-1234-1234-1234-12345678901{5+i}"),
            title=job_data["title"],
            description=job_data["description"],
            requirements=job_data["requirements"],
            parsed_requirements={
                "required_skills": job_data["requirements"],
                "experience_required": 3 if i == 0 else 2,
                "education_required": "Bachelor's degree"
            },
            department=job_data["department"],
            location=job_data["location"],
            employment_type=job_data["employment_type"],
            salary_min=job_data["salary_min"],
            salary_max=job_data["salary_max"],
            organization_id=org.id,
            created_by=recruiter.id,
            status="open"
        )
        db.add(job)
        jobs.append(job)
    
    # Create demo candidates
    candidates_data = [
        {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice.johnson@email.com",
            "skills": ["Python", "React", "AWS", "Docker", "JavaScript"],
            "experience_years": 6,
            "current_company": "TechStart Inc",
            "current_title": "Senior Developer",
            "location": "San Francisco, CA"
        },
        {
            "first_name": "Bob",
            "last_name": "Smith",
            "email": "bob.smith@email.com",
            "skills": ["Java", "Spring", "Microservices", "Kubernetes", "SQL"],
            "experience_years": 8,
            "current_company": "Enterprise Corp",
            "current_title": "Software Architect",
            "location": "New York, NY"
        },
        {
            "first_name": "Carol",
            "last_name": "Davis",
            "email": "carol.davis@email.com",
            "skills": ["Product Strategy", "Agile", "Roadmap Planning", "Analytics"],
            "experience_years": 5,
            "current_company": "ProductCo",
            "current_title": "Senior Product Manager",
            "location": "Seattle, WA"
        },
        {
            "first_name": "David",
            "last_name": "Wilson",
            "email": "david.wilson@email.com",
            "skills": ["Machine Learning", "Python", "TensorFlow", "Statistics", "SQL"],
            "experience_years": 4,
            "current_company": "DataTech",
            "current_title": "Data Scientist",
            "location": "Remote"
        },
        {
            "first_name": "Emma",
            "last_name": "Brown",
            "email": "emma.brown@email.com",
            "skills": ["React", "Node.js", "MongoDB", "Express", "JavaScript"],
            "experience_years": 3,
            "current_company": "StartupXYZ",
            "current_title": "Full Stack Developer",
            "location": "Austin, TX"
        }
    ]
    
    candidates = []
    for i, candidate_data in enumerate(candidates_data):
        candidate = Candidate(
            id=uuid.UUID(f"12345678-1234-1234-1234-12345678902{0+i}"),
            first_name=candidate_data["first_name"],
            last_name=candidate_data["last_name"],
            email=candidate_data["email"],
            skills=candidate_data["skills"],
            experience_years=candidate_data["experience_years"],
            current_company=candidate_data["current_company"],
            current_title=candidate_data["current_title"],
            location=candidate_data["location"],
            organization_id=org.id
        )
        db.add(candidate)
        candidates.append(candidate)
    
    # Create demo applications
    applications = []
    for i, candidate in enumerate(candidates):
        for j, job in enumerate(jobs):
            if i % 2 == j % 2:  # Create some variety in applications
                application = Application(
                    id=uuid.UUID(f"12345678-1234-1234-1234-12345678903{len(applications)}"),
                    job_id=job.id,
                    candidate_id=candidate.id,
                    organization_id=org.id,
                    status=ApplicationStatus.NEW if len(applications) % 3 == 0 else 
                           ApplicationStatus.SCREENING if len(applications) % 3 == 1 else 
                           ApplicationStatus.INTERVIEW,
                    fit_score=0.75 + (len(applications) % 5) * 0.05,  # Vary FitScore between 0.75-0.95
                    source="direct"
                )
                db.add(application)
                applications.append(application)
    
    # Create demo interviews
    for i in range(3):
        interview = Interview(
            id=uuid.UUID(f"12345678-1234-1234-1234-12345678904{i}"),
            application_id=applications[i].id if i < len(applications) else applications[0].id,
            candidate_id=applications[i].candidate_id if i < len(applications) else candidates[0].id,
            interviewer_id=recruiter.id,
            scheduled_at=datetime.utcnow() + timedelta(days=i+1),
            duration_minutes=60,
            type="video",
            meeting_link=f"https://meet.example.com/interview/{i}",
            status=InterviewStatus.SCHEDULED
        )
        db.add(interview)
    
    # Create demo campaigns
    campaign = Campaign(
        id=uuid.UUID("12345678-1234-1234-1234-123456789050"),
        name="Senior Engineer Outreach",
        job_id=jobs[0].id,
        template_id="template_001",
        status=CampaignStatus.COMPLETED,
        target_criteria={"skills": ["Python", "React"], "min_experience": 3},
        sent_count=25,
        opened_count=18,
        clicked_count=12,
        replied_count=8,
        organization_id=org.id,
        created_by=recruiter.id
    )
    db.add(campaign)
    
    # Create demo analytics
    analytics = Analytics(
        id=uuid.UUID("12345678-1234-1234-1234-123456789060"),
        organization_id=org.id,
        metric_type="applications",
        metric_name="total_applications",
        value=len(applications),
        date=datetime.utcnow()
    )
    db.add(analytics)
    
    # Create demo notifications
    notification1 = Notification(
        id=uuid.UUID("12345678-1234-1234-1234-123456789070"),
        user_id=recruiter.id,
        type="application",
        title="New Application Received",
        message="Alice Johnson applied for Senior Software Engineer position",
        data={"application_id": str(applications[0].id), "job_title": jobs[0].title}
    )
    db.add(notification1)
    
    notification2 = Notification(
        id=uuid.UUID("12345678-1234-1234-1234-123456789071"),
        user_id=recruiter.id,
        type="interview",
        title="Interview Tomorrow",
        message="You have an interview scheduled with Bob Smith",
        data={"interview_id": "12345678-1234-1234-1234-123456789040", "candidate_name": "Bob Smith"}
    )
    db.add(notification2)
    
    db.commit()
    print("Demo data generated successfully!")
    
    # Print summary
    print(f"\nDemo Data Summary:")
    print(f"Organization: {org.name}")
    print(f"Users: 2 (Admin: admin@techcorp.com, Recruiter: recruiter@techcorp.com)")
    print(f"Password for all users: 'password123'")
    print(f"Jobs: {len(jobs)} open positions")
    print(f"Candidates: {len(candidates)} in database")
    print(f"Applications: {len(applications)} submitted")
    print(f"Interviews: 3 scheduled")
    print(f"Campaigns: 1 completed outreach campaign")
    print(f"Notifications: 2 recent notifications")

# Helper function to create sample resumes
def create_sample_resume(candidate_name: str, skills: List[str], experience: int) -> str:
    """Create a sample resume text for demo purposes"""
    return f"""
    {candidate_name}
    Email: {candidate_name.lower().replace(' ', '.')}@email.com
    Phone: (555) 123-4567
    Location: San Francisco, CA
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with {experience} years of experience in developing 
    scalable applications. Proficient in {', '.join(skills[:3])} and passionate about 
    building high-quality software solutions.
    
    SKILLS
    Technical Skills: {', '.join(skills)}
    
    EXPERIENCE
    Senior Software Engineer | Tech Company | 2020-Present
    - Developed and maintained web applications using modern frameworks
    - Collaborated with cross-functional teams to deliver projects
    - Mentored junior developers and conducted code reviews
    
    Software Engineer | Startup Inc | 2018-2020
    - Built scalable backend services
    - Implemented automated testing and CI/CD pipelines
    - Participated in agile development processes
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology, 2018
    
    CERTIFICATIONS
    - AWS Certified Developer
    - Scrum Master Certification
    """

def calculate_fit_score_simple(job_skills: List[str], candidate_skills: List[str]) -> float:
    """Simple FitScore calculation for demo"""
    if not job_skills or not candidate_skills:
        return 0.0
    
    job_set = set(skill.lower() for skill in job_skills)
    candidate_set = set(skill.lower() for skill in candidate_skills)
    
    matches = len(job_set.intersection(candidate_set))
    return matches / len(job_set)