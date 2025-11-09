# AI Recruiting Platform - API Documentation

## 🚀 Overview

The AI Recruiting Platform provides a comprehensive REST API for managing the entire recruiting workflow with AI-powered features.

**Base URL**: `https://ai-recruiting-platform.vercel.app/api`

**Authentication**: Bearer token (JWT)

**Content-Type**: `application/json`

## 🔐 Authentication

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "12345678-1234-1234-1234-123456789012",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "recruiter",
    "organization_id": "12345678-1234-1234-1234-123456789013"
  }
}
```

### Register User

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "recruiter",
  "organization_id": "12345678-1234-1234-1234-123456789013"
}
```

## 📋 Job Management

### Create Job

```http
POST /api/jobs
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "description": "We are looking for a Senior Software Engineer...",
  "requirements": ["Python", "React", "AWS", "Docker"],
  "department": "Engineering",
  "location": "San Francisco, CA",
  "employment_type": "Full-time",
  "salary_min": 120000,
  "salary_max": 180000
}
```

**Response**: Job object with AI-parsed requirements

### Get Jobs

```http
GET /api/jobs?skip=0&limit=10
Authorization: Bearer <token>
```

**Query Parameters**:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

### Get Job Details

```http
GET /api/jobs/{job_id}
Authorization: Bearer <token>
```

## 👥 Candidate Management

### Create Candidate

```http
POST /api/candidates
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "candidate@example.com",
  "first_name": "Alice",
  "last_name": "Johnson",
  "phone": "+1-555-123-4567",
  "skills": ["Python", "React", "Node.js"],
  "experience_years": 5,
  "current_company": "Tech Corp",
  "current_title": "Software Engineer",
  "location": "San Francisco, CA"
}
```

### Upload Resume

```http
POST /api/candidates/upload-resume
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Fields:
- file: Resume file (PDF, DOCX, TXT)
- candidate_id: Candidate ID
```

**Response**: Candidate object with parsed resume data

### Search Candidates

```http
GET /api/candidates?query=python&skills=react,nodejs&limit=20
Authorization: Bearer <token>
```

**Query Parameters**:
- `query`: Search query for name, company, or title
- `skills`: Comma-separated list of required skills
- `location`: Location filter
- `min_experience`: Minimum years of experience
- `limit`: Maximum number of results

## 🎯 AI Features

### Calculate FitScore

```http
POST /api/fit-score
Authorization: Bearer <token>
Content-Type: application/json

{
  "job_id": "12345678-1234-1234-1234-123456789012",
  "candidate_id": "12345678-1234-1234-1234-123456789013"
}
```

**Response**:
```json
{
  "application_id": "12345678-1234-1234-1234-123456789014",
  "job_id": "12345678-1234-1234-1234-123456789012",
  "candidate_id": "12345678-1234-1234-1234-123456789013",
  "overall_score": 0.85,
  "skill_match": 0.9,
  "experience_match": 0.8,
  "education_match": 0.75,
  "location_match": 1.0,
  "culture_fit": 0.8,
  "breakdown": {
    "job_analysis": {
      "title": "Senior Software Engineer",
      "required_skills": ["Python", "React", "AWS"],
      "experience_required": 5
    },
    "candidate_analysis": {
      "name": "Alice Johnson",
      "skills": ["Python", "React", "Node.js", "Docker"],
      "experience_years": 5,
      "current_role": "Software Engineer"
    }
  },
  "recommendations": [
    "Excellent skill match for Python and React",
    "Strong experience alignment",
    "Consider for interview"
  ],
  "generated_at": "2024-01-01T12:00:00Z"
}
```

### Get Top Candidates

```http
GET /api/jobs/{job_id}/top-candidates?limit=10
Authorization: Bearer <token>
```

## 📧 Email Campaigns

### Create Campaign

```http
POST /api/campaigns
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Senior Engineer Outreach",
  "job_id": "12345678-1234-1234-1234-123456789012",
  "template_id": "template_001",
  "target_criteria": {
    "skills": ["Python", "React"],
    "min_experience": 3,
    "location": "San Francisco"
  }
}
```

### Launch Campaign

```http
POST /api/campaigns/{campaign_id}/launch
Authorization: Bearer <token>
```

## 📅 Interview Management

### Schedule Interview

```http
POST /api/interviews
Authorization: Bearer <token>
Content-Type: application/json

{
  "application_id": "12345678-1234-1234-1234-123456789012",
  "candidate_id": "12345678-1234-1234-1234-123456789013",
  "interviewer_id": "12345678-1234-1234-1234-123456789014",
  "scheduled_at": "2024-01-15T14:00:00Z",
  "duration_minutes": 60,
  "type": "video",
  "notes": "Technical interview focusing on Python and React"
}
```

### Get Upcoming Interviews

```http
GET /api/interviews/upcoming?days_ahead=7
Authorization: Bearer <token>
```

### Conduct Interview (AI-Assisted)

```http
POST /api/interviews/{interview_id}/conduct
Authorization: Bearer <token>
```

**Response**: AI-generated interview questions

```json
{
  "interview_id": "12345678-1234-1234-1234-123456789015",
  "questions": [
    {
      "type": "technical",
      "question": "Explain the difference between state and props in React",
      "follow_up": "Can you give an example of when you would use each?"
    },
    {
      "type": "experience",
      "question": "Tell me about a challenging project you worked on",
      "follow_up": "What would you do differently if you did it again?"
    }
  ],
  "meeting_link": "https://meet.example.com/interview/12345678",
  "status": "in_progress"
}
```

## 📊 Analytics

### Get Dashboard Data

```http
GET /api/analytics/dashboard
Authorization: Bearer <token>
```

**Response**:
```json
{
  "total_jobs": 15,
  "active_jobs": 8,
  "total_candidates": 120,
  "total_applications": 45,
  "applications_by_status": {
    "new": 15,
    "screening": 12,
    "interview": 10,
    "offer": 5,
    "hired": 3
  },
  "average_fit_score": 0.78,
  "time_to_hire_avg": 21.5,
  "conversion_rates": {
    "new_to_screening": 0.8,
    "screening_to_interview": 0.6,
    "interview_to_offer": 0.4,
    "offer_to_hired": 0.75
  },
  "top_skills": [
    {"skill": "python", "count": 25},
    {"skill": "react", "count": 20},
    {"skill": "javascript", "count": 18}
  ],
  "recent_activity": [
    {
      "type": "application",
      "description": "New application received",
      "timestamp": "2024-01-01T12:00:00Z",
      "details": {
        "candidate_name": "Alice Johnson",
        "job_title": "Senior Software Engineer"
      }
    }
  ]
}
```

### Get Detailed Analytics

```http
GET /api/analytics/detailed?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

## 🔔 Notifications

### Get Notifications

```http
GET /api/notifications
Authorization: Bearer <token>
```

### Mark as Read

```http
POST /api/notifications/{notification_id}/read
Authorization: Bearer <token>
```

## 🛠️ Error Handling

### Error Response Format

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": {
    "field": "email",
    "reason": "Email already exists"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## 📚 Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication**: 10 requests per minute
- **Job operations**: 100 requests per hour
- **AI features**: 50 requests per hour
- **Email campaigns**: 5 campaigns per hour

## 🔒 Security

- All endpoints require authentication except `/health`
- JWT tokens expire after 30 minutes
- Passwords are hashed using bcrypt
- SQL injection protection via SQLAlchemy ORM
- CORS configured for cross-origin requests
- File upload size limited to 10MB

## 📖 Examples

### Complete Workflow: Post Job → Find Candidates → Hire

```bash
# 1. Create a job
curl -X POST https://ai-recruiting-platform.vercel.app/api/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Backend Developer",
    "description": "Looking for Python developer...",
    "requirements": ["Python", "Django", "PostgreSQL"]
  }'

# 2. Search for candidates
curl -X GET "https://ai-recruiting-platform.vercel.app/api/candidates?skills=python,django&min_experience=3" \
  -H "Authorization: Bearer $TOKEN"

# 3. Calculate FitScore for top candidates
curl -X POST https://ai-recruiting-platform.vercel.app/api/fit-score \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "job-id",
    "candidate_id": "candidate-id"
  }'

# 4. Schedule interview
curl -X POST https://ai-recruiting-platform.vercel.app/api/interviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "application-id",
    "candidate_id": "candidate-id",
    "interviewer_id": "interviewer-id",
    "scheduled_at": "2024-01-15T14:00:00Z"
  }'

# 5. Complete hiring process
curl -X PATCH https://ai-recruiting-platform.vercel.app/api/applications/application-id \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "hired"}'
```

---

This API documentation covers all the endpoints available in the AI Recruiting Platform. For more detailed information, visit the interactive API documentation at `/docs` when running the application locally.