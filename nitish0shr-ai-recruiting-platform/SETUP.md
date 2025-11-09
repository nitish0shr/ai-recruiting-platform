# AI Recruiting Platform - Setup Guide

## 🚀 Quick Start

This guide will help you set up the AI Recruiting Platform for local development or production deployment.

## 📋 Prerequisites

- **Node.js** 18+ and **npm**
- **Python** 3.11+
- **PostgreSQL** 15+
- **Redis** (for caching and sessions)
- **OpenAI API Key**

## 🔧 Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/nitish0shr/ai-recruiting-platform.git
cd ai-recruiting-platform
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd apps/backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### Environment Configuration

Create a `.env` file in the backend directory:

```bash
cp .env.sample .env
```

Update the environment variables:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/ai_recruiting

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Security
SECRET_KEY=your-secret-key-here

# Email (Optional)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Demo Data
GENERATE_DEMO_DATA=true
```

#### Database Setup

```bash
# Create database
createdb ai_recruiting

# Run migrations
alembic upgrade head

# Generate demo data (optional)
python -c "from src.database import get_db; from src.utils import generate_demo_data; db = next(get_db()); generate_demo_data(db); db.close()"
```

#### Start Backend Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

### 3. Frontend Setup

#### Install Dependencies

```bash
cd apps/frontend
npm install
```

#### Environment Configuration

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Start Frontend Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## 🐳 Docker Setup

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

### Individual Services

```bash
# Backend only
docker build -t ai-recruiting-backend apps/backend
docker run -p 8000:8000 ai-recruiting-backend

# Frontend only
docker build -t ai-recruiting-frontend apps/frontend
docker run -p 3000:3000 ai-recruiting-frontend
```

## 🚀 Production Deployment

### Vercel Deployment

1. **Connect Repository to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com)
   - Import your GitHub repository
   - Vercel will auto-detect the monorepo structure

2. **Environment Variables**
   Add these to your Vercel project settings:

   ```
   DATABASE_URL=postgresql://...
   OPENAI_API_KEY=sk-...
   SECRET_KEY=your-secret-key
   SMTP_USERNAME=your-email
   SMTP_PASSWORD=your-password
   REDIS_URL=redis://...
   ```

3. **Deploy**
   ```bash
git push origin main
```

Vercel will automatically deploy both frontend and backend.

### Manual Deployment

#### Backend (Any Cloud Provider)

```bash
# Build Docker image
docker build -t ai-recruiting-backend apps/backend

# Push to container registry
docker tag ai-recruiting-backend your-registry/ai-recruiting-backend
docker push your-registry/ai-recruiting-backend

# Deploy to your cloud provider
# Configure environment variables and database connections
```

#### Frontend (Static Hosting)

```bash
cd apps/frontend
npm run build

# Deploy to Vercel
npx vercel --prod

# Or deploy to Netlify
npx netlify deploy --prod --dir=out
```

## 🔐 Demo Accounts

After setting up demo data, you can use these accounts:

- **Admin**: `admin@techcorp.com` / `password123`
- **Recruiter**: `recruiter@techcorp.com` / `password123`

## 📊 Database Schema

The platform uses PostgreSQL with the following main tables:

- `organizations` - Company/tenant information
- `users` - Platform users with role-based access
- `jobs` - Job postings with AI-parsed requirements
- `candidates` - Candidate profiles with parsed resumes
- `applications` - Job applications with FitScores
- `interviews` - Scheduled interviews and feedback
- `campaigns` - Email outreach campaigns
- `analytics` - Performance metrics and insights

## 🔧 Configuration Options

### Feature Flags

Configure features in your environment:

```env
# AI Features
FIT_SCORE_THRESHOLD=0.7
MAX_CANDIDATES_PER_JOB=100

# Integrations
GOOGLE_CALENDAR_ENABLED=false
OUTLOOK_CALENDAR_ENABLED=false

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_FILE_SIZE=10485760  # 10MB
```

### Customization

- **Branding**: Modify `apps/frontend/src/app/globals.css` for custom styling
- **Email Templates**: Update templates in `apps/backend/src/services/email_service.py`
- **AI Prompts**: Customize prompts in AI service files
- **Analytics**: Extend metrics in `apps/backend/src/services/analytics_service.py`

## 🛠️ Development Tips

### Debugging

```bash
# Backend logs
 tail -f apps/backend/logs/app.log

# Frontend console
npm run dev -- --verbose
```

### Testing

```bash
# Backend tests
cd apps/backend
pytest tests/ -v

# Frontend tests
cd apps/frontend
npm test
```

### Database Management

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📞 Support

For issues and questions:

1. Check the [Issues](https://github.com/nitish0shr/ai-recruiting-platform/issues) page
2. Review API documentation at `/docs` when running locally
3. Check component documentation in source code

## 🎯 Next Steps

1. **Customize for your organization** - Update branding, workflows
2. **Integrate with existing systems** - Connect to HRIS, ATS
3. **Add more AI features** - Video interviews, skill assessments
4. **Scale infrastructure** - Add caching, monitoring, auto-scaling
5. **Train custom models** - Fine-tune AI on your company's data

---

This platform is production-ready and can handle real recruiting workflows with AI-powered automation. Start with the demo data to explore all features!