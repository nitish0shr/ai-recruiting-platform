# AI Recruiting Platform

A production-grade AI recruiting platform with automated sourcing, scoring, and outreach capabilities.

## Features

### Core Functionality
- **Job Description Parsing**: AI-powered extraction of structured data from job descriptions
- **Resume Parsing**: OCR-backed resume parsing with multiple format support
- **FitScore Calculation**: Intelligent candidate-job matching with explainable scoring
- **Automated Outreach**: Multi-step email sequences with personalization
- **Pipeline Management**: Kanban-style candidate pipeline with drag-and-drop
- **Interview Scheduling**: Automated 3-slot interview scheduling with calendar integration
- **Analytics & Reporting**: Real-time dashboards and recruitment funnel analysis
- **Health Monitoring**: Automated pipeline health tracking with sourcing triggers

### Technical Features
- **Microservices Architecture**: Separate services for frontend, backend, and ML
- **API-First Design**: OpenAPI v3 compliant REST APIs
- **Real-time Updates**: WebSocket connections for live pipeline updates
- **Security**: RBAC, encryption, webhook HMAC validation
- **Scalability**: Redis caching, database connection pooling
- **Observability**: Structured logging, metrics, and health checks

## Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom design system
- **State Management**: TanStack Query (React Query)
- **UI Components**: Headless UI, Radix UI primitives
- **Charts**: Recharts for data visualization
- **Animations**: Framer Motion for smooth transitions

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session management and caching
- **Task Queue**: Celery for background job processing
- **Authentication**: JWT tokens with refresh mechanism

### AI/ML Services
- **NLP**: spaCy for text processing
- **Embeddings**: OpenAI and Hugging Face models
- **OCR**: Tesseract for image-based text extraction
- **Vector Search**: FAISS for similarity matching

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for local development
- **CI/CD**: GitHub Actions with automated testing
- **Cloud**: Ready for AWS/GCP/Azure deployment

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (or use Docker)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ai-recruiting-platform.git
   cd ai-recruiting-platform
   ```

2. **Set up environment variables**
   ```bash
   cp .env.sample .env
   # Edit .env with your configuration
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development without Docker

1. **Backend setup**
   ```bash
   cd apps/backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Frontend setup**
   ```bash
   cd apps/frontend
   npm install
   npm run dev
   ```

## Project Structure

```
ai-recruiting-platform/
├── apps/
│   ├── frontend/          # Next.js frontend application
│   ├── backend/           # FastAPI backend application
│   └── ml/               # Machine learning services
├── packages/
│   ├── contracts/         # OpenAPI contracts and types
│   └── ui/               # Shared UI components
├── tests/                # Test suites
├── ops/                  # Infrastructure and deployment
├── datasets/             # Sample data and models
└── docs/                 # Documentation
```

## API Documentation

The API follows RESTful principles and is documented using OpenAPI v3. Access the interactive documentation at:
- Development: http://localhost:8000/docs
- Swagger UI: http://localhost:8000/redoc

### Key Endpoints

- `POST /jobs` - Create a new job from JD
- `GET /jobs/{id}/publish` - Publish job to career page
- `POST /candidates` - Ingest candidate from resume
- `POST /candidates/{id}/score` - Calculate FitScore
- `POST /pipeline/move` - Move candidate between stages
- `POST /outreach/send` - Send outreach message
- `POST /schedule/propose` - Propose interview slots
- `POST /schedule/confirm` - Confirm interview slot

## Configuration

### Environment Variables

Required environment variables (see `.env.sample`):

```bash
# Application
NEXT_PUBLIC_APP_URL=https://your-domain.com
API_URL=https://api.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# AI Services
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_TOKEN=your-hf-token

# Storage
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET=resumes

# Security
JWT_SECRET=your-jwt-secret
ENCRYPTION_AT_REST_KEY=your-encryption-key
WEBHOOK_HMAC_SECRET=your-hmac-secret
```

## Deployment

### Docker Deployment

1. **Build images**
   ```bash
   docker-compose build
   ```

2. **Push to registry**
   ```bash
   docker-compose push
   ```

3. **Deploy to production**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Cloud Deployment

The platform is designed to be cloud-agnostic and can be deployed to:
- **AWS**: ECS, EKS, or Lambda
- **Google Cloud**: Cloud Run, GKE, or App Engine
- **Azure**: Container Apps, AKS, or App Service

### CI/CD Pipeline

The repository includes a comprehensive GitHub Actions workflow that:
- Validates OpenAPI contracts
- Runs backend tests (pytest)
- Runs frontend tests (Jest)
- Performs security scanning
- Builds and pushes Docker images
- Deploys to staging and production
- Runs acceptance and accessibility tests

## Testing

### Backend Tests
```bash
cd apps/backend
pytest --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd apps/frontend
npm test
```

### Integration Tests
```bash
# Run full test suite
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Monitoring & Observability

### Health Checks
- Application health: `GET /health`
- Database connectivity
- Redis connectivity
- External service dependencies

### Logging
- Structured logging with correlation IDs
- PII redaction in logs
- Centralized log aggregation ready

### Metrics
- Application performance metrics
- Business metrics (conversion rates, time-to-hire)
- Infrastructure metrics
- Custom dashboards available

## Security

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Organization-level isolation

### Data Protection
- Encryption at rest and in transit
- PII masking and redaction
- Audit logging
- GDPR compliance features

### API Security
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection
- HMAC webhook validation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation
- Ensure accessibility compliance
- Maintain backward compatibility

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Contact the development team

## Roadmap

### Upcoming Features
- [ ] Advanced ML model integration
- [ ] Video interview analysis
- [ ] Predictive analytics
- [ ] Mobile application
- [ ] Advanced reporting
- [ ] Integration marketplace

### Performance Improvements
- [ ] GraphQL API implementation
- [ ] Microservices optimization
- [ ] Edge computing support
- [ ] Advanced caching strategies

---

Built with ❤️ by the AI Recruiting Platform Team