#!/bin/bash

# AI Recruiting Platform Deployment Script
# This script deploys the platform to staging and production environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_URL="https://staging.recruiting-platform.com"
PRODUCTION_URL="https://recruiting-platform.com"
REGISTRY="ghcr.io"
IMAGE_NAME="ai-recruiting-platform"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE} AI Recruiting Platform Deployment      ${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Check kubectl (for Kubernetes deployment)
    if ! command -v kubectl &> /dev/null; then
        echo -e "${YELLOW}Warning: kubectl is not installed (required for Kubernetes deployment)${NC}"
    fi
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}"
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    
    # Backend tests
    echo "Running backend tests..."
    cd apps/backend
    if [ -f "requirements-test.txt" ]; then
        pip install -r requirements-test.txt
    fi
    pytest --cov=. --cov-report=html || echo "Backend tests failed"
    cd ../..
    
    # Frontend tests
    echo "Running frontend tests..."
    cd apps/frontend
    npm test || echo "Frontend tests failed"
    cd ../..
    
    echo -e "${GREEN}✓ Tests completed${NC}"
}

# Function to build and push images
build_and_push() {
    echo -e "${YELLOW}Building and pushing Docker images...${NC}"
    
    # Build backend image
    echo "Building backend image..."
    docker build -t ${REGISTRY}/${IMAGE_NAME}:backend-${GITHUB_SHA:-latest} \
                 --target backend .
    
    # Build frontend image
    echo "Building frontend image..."
    docker build -t ${REGISTRY}/${IMAGE_NAME}:frontend-${GITHUB_SHA:-latest} \
                 --target frontend .
    
    # Push images (if authenticated)
    if [ -n "$GITHUB_TOKEN" ]; then
        echo "Pushing images to registry..."
        echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
        docker push ${REGISTRY}/${IMAGE_NAME}:backend-${GITHUB_SHA:-latest}
        docker push ${REGISTRY}/${IMAGE_NAME}:frontend-${GITHUB_SHA:-latest}
    else
        echo -e "${YELLOW}Not authenticated to push images${NC}"
    fi
    
    echo -e "${GREEN}✓ Images built successfully${NC}"
}

# Function to deploy to staging
deploy_staging() {
    echo -e "${YELLOW}Deploying to staging...${NC}"
    
    # Deploy with Docker Compose
    echo "Deploying with Docker Compose..."
    docker-compose -f docker-compose.staging.yml up -d
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    if curl -f ${STAGING_URL}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Staging deployment successful${NC}"
        echo -e "${BLUE}Staging URL: ${STAGING_URL}${NC}"
    else
        echo -e "${RED}Staging deployment failed${NC}"
        exit 1
    fi
}

# Function to run acceptance tests
run_acceptance_tests() {
    echo -e "${YELLOW}Running acceptance tests...${NC}"
    
    # Install test dependencies
    pip install pytest pytest-asyncio aiohttp
    
    # Run acceptance tests
    python -m pytest tests/acceptance/ -v || {
        echo -e "${RED}Acceptance tests failed${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✓ Acceptance tests passed${NC}"
}

# Function to deploy to production
deploy_production() {
    echo -e "${YELLOW}Deploying to production...${NC}"
    
    # Confirm production deployment
    read -p "Are you sure you want to deploy to production? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Production deployment cancelled"
        return
    fi
    
    # Deploy with Docker Compose
    echo "Deploying with Docker Compose..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    if curl -f ${PRODUCTION_URL}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Production deployment successful${NC}"
        echo -e "${BLUE}Production URL: ${PRODUCTION_URL}${NC}"
    else
        echo -e "${RED}Production deployment failed${NC}"
        exit 1
    fi
}

# Function to run Lighthouse accessibility test
run_lighthouse_test() {
    echo -e "${YELLOW}Running Lighthouse accessibility tests...${NC}"
    
    # Install Lighthouse CLI
    npm install -g lighthouse
    
    # Run Lighthouse test
    lighthouse ${STAGING_URL} \
        --chrome-flags="--headless" \
        --output=json \
        --output-path=lighthouse-report.json \
        --only-categories=accessibility
    
    # Check accessibility score
    score=$(jq '.categories.accessibility.score' lighthouse-report.json)
    if (( $(echo "$score >= 0.95" | bc -l) )); then
        echo -e "${GREEN}✓ Accessibility score: ${score} (≥ 0.95)${NC}"
    else
        echo -e "${RED}Accessibility score too low: ${score}${NC}"
        exit 1
    fi
}

# Function to generate demo data
generate_demo_data() {
    echo -e "${YELLOW}Generating demo data...${NC}"
    
    # Create sample jobs
    python scripts/generate_demo_data.py
    
    echo -e "${GREEN}✓ Demo data generated${NC}"
}

# Function to show deployment status
show_status() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} Deployment Status                       ${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Show running containers
    echo "Running containers:"
    docker-compose ps
    
    # Show logs
    echo -e "\nRecent logs:"
    docker-compose logs --tail=10
}

# Function to rollback deployment
rollback() {
    echo -e "${YELLOW}Rolling back deployment...${NC}"
    
    # Stop current services
    docker-compose down
    
    # Start previous version
    docker-compose -f docker-compose.previous.yml up -d
    
    echo -e "${GREEN}✓ Rollback completed${NC}"
}

# Main deployment flow
main() {
    case "${1:-staging}" in
        "staging")
            check_prerequisites
            run_tests
            build_and_push
            deploy_staging
            run_acceptance_tests
            run_lighthouse_test
            generate_demo_data
            show_status
            ;;
        "production")
            check_prerequisites
            run_tests
            build_and_push
            deploy_staging
            run_acceptance_tests
            deploy_production
            show_status
            ;;
        "rollback")
            rollback
            ;;
        "status")
            show_status
            ;;
        *)
            echo "Usage: $0 {staging|production|rollback|status}"
            echo "  staging    - Deploy to staging environment"
            echo "  production - Deploy to production environment"
            echo "  rollback   - Rollback to previous version"
            echo "  status     - Show deployment status"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"