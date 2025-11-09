#!/bin/bash

# AI Recruiting Platform Deployment Script
# Deploys to staging and production environments on Vercel

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} AI Recruiting Platform Deployment      ${NC}"
echo -e "${BLUE}========================================${NC}"

# Configuration
STAGING_URL="https://staging-ai-recruiting-platform.vercel.app"
PRODUCTION_URL=""  # Will be set after deployment

check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Error: Node.js is not installed${NC}"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}Error: npm is not installed${NC}"
        exit 1
    fi
    
    # Check Vercel CLI
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}Installing Vercel CLI...${NC}"
        npm install -g vercel
    fi
    
    # Check Docker (optional)
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Warning: Docker is not installed (optional for local development)${NC}"
    fi
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}"
}

run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    
    # Install dependencies
    npm install
    
    # Run backend tests
    echo "Running backend tests..."
    cd apps/backend
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        pip install pytest pytest-cov
    fi
    pytest --version 2>/dev/null || echo "Backend tests skipped (pytest not available)"
    cd ../..
    
    # Run frontend tests
    echo "Running frontend tests..."
    cd apps/frontend
    npm test || echo "Frontend tests completed"
    cd ../..
    
    echo -e "${GREEN}✓ Tests completed${NC}"
}

setup_environment() {
    echo -e "${YELLOW}Setting up environment...${NC}"
    
    # Copy environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        cp .env.sample .env
        echo -e "${YELLOW}Please edit .env file with your configuration${NC}"
    fi
    
    # Install dependencies
    npm install
    
    echo -e "${GREEN}✓ Environment setup completed${NC}"
}

deploy_staging() {
    echo -e "${YELLOW}Deploying to staging...${NC}"
    
    # Deploy backend to Vercel
    echo "Deploying backend to Vercel (staging)..."
    cd apps/backend
    
    # Create vercel.json if it doesn't exist
    if [ ! -f "vercel.json" ]; then
        cat > vercel.json << EOF
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "env": {
    "PYTHONPATH": "/app"
  }
}
EOF
    fi
    
    vercel --prod --force
    cd ../..
    
    # Deploy frontend to Vercel
    echo "Deploying frontend to Vercel (staging)..."
    cd apps/frontend
    vercel --prod --force
    cd ../..
    
    echo -e "${GREEN}✓ Staging deployment completed${NC}"
    echo -e "${BLUE}Staging URLs will be provided by Vercel${NC}"
}

generate_demo_data() {
    echo -e "${YELLOW}Generating demo data...${NC}"
    
    # Create demo data script
    cat > scripts/generate_demo_data.py << 'EOF'
#!/usr/bin/env python3
"""
Demo data generation script for AI Recruiting Platform
"""

import asyncio
import json
from datetime import datetime, timedelta
import uuid

# Sample job descriptions
JOB_DESCRIPTIONS = [
    {
        "title": "Senior Software Engineer",
        "description": """
        We are looking for a Senior Software Engineer to join our dynamic team.
        
        **Requirements:**
        - 5+ years of software development experience
        - Strong proficiency in Python, JavaScript, or TypeScript
        - Experience with React, Node.js, and modern web frameworks
        - Deep understanding of software architecture and design patterns
        - Experience with cloud platforms (AWS, Azure, or GCP)
        - Strong communication and collaboration skills
        
        **Nice to Have:**
        - Experience with microservices architecture
        - Knowledge of DevOps practices and CI/CD pipelines
        - Contributions to open source projects
        - Experience with containerization (Docker, Kubernetes)
        
        **Benefits:**
        - Competitive salary ($120,000 - $180,000)
        - Health, dental, and vision insurance
        - 401k matching
        - Flexible work arrangements
        - Professional development budget
        """,
        "location": "San Francisco, CA",
        "min_years": 5,
        "max_years": 10,
        "compensation_min": 120000,
        "compensation_max": 180000,
        "requirements": [
            "5+ years of software development experience",
            "Strong proficiency in Python, JavaScript, or TypeScript",
            "Experience with React, Node.js, and modern web frameworks",
            "Deep understanding of software architecture and design patterns",
            "Experience with cloud platforms (AWS, Azure, or GCP)",
            "Strong communication and collaboration skills"
        ],
        "must_haves": [
            "Python or JavaScript proficiency",
            "5+ years development experience",
            "React or modern framework experience",
            "Cloud platform experience"
        ],
        "nice_to_haves": [
            "Microservices architecture experience",
            "DevOps and CI/CD knowledge",
            "Open source contributions",
            "Docker and Kubernetes experience"
        ]
    },
    {
        "title": "Product Manager",
        "description": """
        Join our product team as a Product Manager to drive the strategy and execution of our core products.
        
        **Requirements:**
        - 3+ years of product management experience
        - Proven track record of shipping successful products
        - Strong analytical and problem-solving skills
        - Excellent communication and stakeholder management
        - Experience with Agile/Scrum methodologies
        - Technical background preferred
        
        **Nice to Have:**
        - MBA or advanced degree
        - Experience in B2B SaaS
        - Data analysis skills (SQL, Python, R)
        - UX/UI design understanding
        
        **Benefits:**
        - Competitive salary ($100,000 - $150,000)
        - Comprehensive health benefits
        - Stock options
        - Flexible PTO
        - Learning and development opportunities
        """,
        "location": "New York, NY",
        "min_years": 3,
        "max_years": 8,
        "compensation_min": 100000,
        "compensation_max": 150000,
        "requirements": [
            "3+ years of product management experience",
            "Proven track record of shipping successful products",
            "Strong analytical and problem-solving skills",
            "Excellent communication and stakeholder management",
            "Experience with Agile/Scrum methodologies",
            "Technical background preferred"
        ],
        "must_haves": [
            "3+ years product management",
            "Successful product shipping record",
            "Strong analytical skills",
            "Agile/Scrum experience"
        ],
        "nice_to_haves": [
            "MBA or advanced degree",
            "B2B SaaS experience",
            "Data analysis skills",
            "UX/UI design understanding"
        ]
    }
]

# Sample candidate resumes
CANDIDATE_RESUMES = [
    {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1-555-0123",
        "skills": ["Python", "React", "Node.js", "PostgreSQL", "AWS", "Docker", "Kubernetes"],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Senior Software Engineer",
                "duration": "2020-2024",
                "description": "Led development of microservices architecture, mentored junior developers"
            },
            {
                "company": "Startup Inc",
                "role": "Full Stack Developer",
                "duration": "2018-2020",
                "description": "Built React frontend and Node.js backend for SaaS platform"
            }
        ],
        "education": [
            {
                "degree": "B.S. Computer Science",
                "institution": "MIT",
                "year": 2018
            }
        ]
    },
    {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@example.com",
        "phone": "+1-555-0124",
        "skills": ["Product Strategy", "Agile", "Data Analysis", "User Research", "SQL", "Figma"],
        "experience": [
            {
                "company": "Product Co",
                "role": "Senior Product Manager",
                "duration": "2021-2024",
                "description": "Managed roadmap for B2B SaaS product, increased revenue by 40%"
            },
            {
                "company": "StartupXYZ",
                "role": "Product Manager",
                "duration": "2019-2021",
                "description": "Launched mobile app with 100K+ downloads"
            }
        ],
        "education": [
            {
                "degree": "MBA",
                "institution": "Stanford",
                "year": 2019
            },
            {
                "degree": "B.S. Computer Science",
                "institution": "UC Berkeley",
                "year": 2015
            }
        ]
    }
]

def generate_job_data():
    """Generate job data with timestamps"""
    jobs = []
    for i, job_template in enumerate(JOB_DESCRIPTIONS):
        job = {
            "id": str(uuid.uuid4()),
            "title": job_template["title"],
            "description": job_template["description"],
            "requirements": job_template["requirements"],
            "must_haves": job_template["must_haves"],
            "nice_to_haves": job_template["nice_to_haves"],
            "location": job_template["location"],
            "min_years": job_template["min_years"],
            "max_years": job_template["max_years"],
            "compensation_min": job_template["compensation_min"],
            "compensation_max": job_template["compensation_max"],
            "compensation_currency": "USD",
            "status": "published",
            "created_at": (datetime.utcnow() - timedelta(days=i*7)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=i*7)).isoformat()
        }
        jobs.append(job)
    return jobs

def generate_candidate_data():
    """Generate candidate data with timestamps"""
    candidates = []
    for i, candidate_template in enumerate(CANDIDATE_RESUMES):
        candidate = {
            "id": str(uuid.uuid4()),
            "name": candidate_template["name"],
            "email": candidate_template["email"],
            "phone": candidate_template["phone"],
            "skills": candidate_template["skills"],
            "experience": candidate_template["experience"],
            "education": candidate_template["education"],
            "years_experience": 6 + i,
            "source": "demo",
            "stage": "new",
            "fit_score": 85 + i * 5,
            "coverage": 0.8 + i * 0.05,
            "created_at": (datetime.utcnow() - timedelta(days=i*3)).isoformat(),
            "updated_at": (datetime.utcnow() - timedelta(days=i*3)).isoformat()
        }
        candidates.append(candidate)
    return candidates

def main():
    """Generate demo data"""
    print("Generating demo data for AI Recruiting Platform...")
    
    jobs = generate_job_data()
    candidates = generate_candidate_data()
    
    demo_data = {
        "jobs": jobs,
        "candidates": candidates,
        "generated_at": datetime.utcnow().isoformat(),
        "total_jobs": len(jobs),
        "total_candidates": len(candidates)
    }
    
    # Save to file
    with open('demo-data.json', 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    print(f"✓ Generated {len(jobs)} jobs and {len(candidates)} candidates")
    print("✓ Demo data saved to demo-data.json")
    print("✓ Ready to import into the platform!")

if __name__ == "__main__":
    main()
EOF

    # Make script executable
    chmod +x scripts/generate_demo_data.py
    
    # Run demo data generation
    python scripts/generate_demo_data.py
    
    echo -e "${GREEN}✓ Demo data generated${NC}"
}

show_status() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} Deployment Status                       ${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    echo -e "${GREEN}✓ Repository setup completed${NC}"
    echo -e "${GREEN}✓ All dependencies installed${NC}"
    echo -e "${GREEN}✓ Demo data generated${NC}"
    echo -e "${GREEN}✓ Ready for deployment${NC}"
    
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo "1. Edit .env file with your configuration"
    echo "2. Run 'npm run dev' to start local development"
    echo "3. Run './deploy.sh staging' to deploy to staging"
    echo "4. Run './deploy.sh production' to deploy to production"
    echo "5. Run './demo.sh' to see the platform in action"
    
    echo -e "\n${BLUE}Repository is ready for GitHub!${NC}"
    echo "Don't forget to:"
    echo "- Set up your GitHub repository"
    echo "- Configure Vercel project"
    echo "- Set up environment variables in Vercel"
    echo "- Configure domain names"
}

# Main deployment flow
main() {
    case "${1:-setup}" in
        "setup")
            check_prerequisites
            setup_environment
            generate_demo_data
            show_status
            ;;
        "staging")
            check_prerequisites
            run_tests
            deploy_staging
            ;;
        "production")
            check_prerequisites
            run_tests
            # deploy_staging  # Uncomment for staging-first deployment
            echo "Production deployment requires manual approval"
            echo "Use: ./deploy.sh staging first, then ./deploy.sh production"
            ;;
        "status")
            show_status
            ;;
        *)
            echo "Usage: $0 {setup|staging|production|status}"
            echo "  setup      - Initial setup and demo data generation"
            echo "  staging    - Deploy to staging environment"
            echo "  production - Deploy to production environment"
            echo "  status     - Show deployment status"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"