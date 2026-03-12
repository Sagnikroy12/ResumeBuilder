# Resume Builder - Deployment & CI/CD Guide

## Overview

This document provides comprehensive instructions for deploying the Resume Builder SaaS application using Docker and GitHub Actions CI/CD pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Setup](#docker-setup)
4. [GitHub Actions CI/CD](#github-actions-cicd)
5. [Deployment Options](#deployment-options)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker Desktop (v20.10+)
- Docker Compose (v1.29+)
- Python 3.9+ (for local development)
- Git
- GitHub account with repository access
- (Optional) Cloud platform account (AWS, GCP, Azure, etc.)

---

## Local Development

### 1. Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your local settings
```

### 2. Run Application Locally (Without Docker)

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask development server
python run.py

# Application will be available at http://localhost:5000
```

### 3. Run Tests Locally

```bash
# Run all tests
pytest tests/

# Run tests with coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_routes.py -v

# Run tests with specific markers
pytest -m unit
```

### 4. Code Quality Checks

```bash
# Format code with black
black app tests

# Check code style with flake8
flake8 app tests

# Sort imports with isort
isort app tests

# Run linting
pylint app

# Check for vulnerabilities
bandit -r app
```

---

## Docker Setup

### 1. Build Docker Image

```bash
# Build image with default name
docker build -t resume-builder:latest .

# Build with custom tag
docker build -t resume-builder:v1.0.0 .

# Build with build args
docker build --build-arg PYTHON_VERSION=3.11 -t resume-builder:latest .
```

### 2. Run Docker Container

```bash
# Run with default settings
docker run -p 5000:5000 resume-builder:latest

# Run with environment variables
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  resume-builder:latest

# Run with volume mounting for uploads
docker run -p 5000:5000 \
  -v /path/to/uploads:/app/uploads \
  resume-builder:latest

# Run in background (detached mode)
docker run -d -p 5000:5000 \
  --name resume-builder \
  resume-builder:latest
```

### 3. Docker Compose Setup (Recommended)

```bash
# Start services in the background
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Rebuild images and start
docker-compose up -d --build

# Run tests in Docker
docker-compose exec web pytest tests/

# Access application shell
docker-compose exec web flask shell
```

### 4. Docker Compose Configuration

The `docker-compose.yml` includes:

- **Web Service**: Flask application running with Gunicorn
- **Volumes**: Persistent uploads directory
- **Networks**: Isolated network for services
- **Health Checks**: Automatic container health monitoring
- **Port Mapping**: Port 5000 exposed for web access

---

## GitHub Actions CI/CD

### 1. Workflows Overview

#### `tests.yml` - Test Pipeline
- Runs on: Push to main/develop, Pull requests
- Tests Python 3.9, 3.10, 3.11
- Includes: Linting, formatting, and unit tests
- Coverage reporting to Codecov

#### `docker.yml` - Docker Build & Push
- Builds Docker image on main/develop push
- Pushes to Docker Hub and GitHub Container Registry
- Automatic tagging based on branch/tag
- Multi-stage build caching

#### `security.yml` - Security Scanning
- Bandit: Python security linting
- Safety: Dependency vulnerability checking
- Trivy: Container image scanning
- Runs on schedule (daily) and on push

#### `quality.yml` - Code Quality Analysis
- Pylint: Code quality analysis
- Radon: Complexity and maintainability metrics
- Optional SonarCloud integration

#### `deploy.yml` - Production Deployment
- Triggered on main branch push or manual workflow_dispatch
- Health checks post-deployment
- Slack notifications

### 2. GitHub Secrets Configuration

Set the following secrets in your GitHub repository settings:

```
DOCKER_USERNAME     - Docker Hub username
DOCKER_PASSWORD     - Docker Hub personal access token
SLACK_WEBHOOK_URL   - Slack webhook for notifications
DEPLOY_KEY          - SSH key for deployment server
```

**To add secrets:**
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with the name and value

### 3. Manual Workflow Trigger

```bash
# Trigger deployment workflow via GitHub CLI
gh workflow run deploy.yml

# Monitor workflow status
gh run list
gh run view <run-id> --log
```

---

## Deployment Options

### Option 1: Deploy to AWS ECS (Elastic Container Service)

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name resume-builder

# 2. Push image to ECR
docker tag resume-builder:latest <account-id>.dkr.ecr.<region>.amazonaws.com/resume-builder:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/resume-builder:latest

# 3. Create ECS task definition and service
# (Use AWS Console or CloudFormation)
```

Update `.github/workflows/deploy.yml` with ECS deployment script.

### Option 2: Deploy to Google Cloud Run

```bash
# 1. Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/resume-builder:latest

# 2. Deploy to Cloud Run
gcloud run deploy resume-builder \
  --image gcr.io/PROJECT-ID/resume-builder:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 3: Deploy to Heroku

```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create your-app-name

# 3. Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key

# 4. Deploy
git push heroku main

# 5. View logs
heroku logs --tail
```

### Option 4: Deploy to Your Own Server

```bash
# 1. SSH into server
ssh user@your-server.com

# 2. Clone repository
git clone https://github.com/yourusername/resume-builder.git

# 3. Pull Docker image
docker pull your-registry/resume-builder:latest

# 4. Run container with systemd or supervisor
# (See systemd service example below)

# 5. Configure reverse proxy (Nginx/Apache)
# (See nginx configuration example below)
```

**Systemd Service Example** (`/etc/systemd/system/resume-builder.service`):

```ini
[Unit]
Description=Resume Builder Application
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=docker
Restart=always
RestartSec=10
ExecStart=/usr/bin/docker run --rm \
  --name resume-builder \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=${SECRET_KEY} \
  -v /opt/resume-builder/uploads:/app/uploads \
  resume-builder:latest

[Install]
WantedBy=multi-user.target
```

**Nginx Reverse Proxy Configuration**:

```nginx
upstream resume_builder {
    server localhost:5000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://resume_builder;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /opt/resume-builder/app/static/;
        expires 30d;
    }
}
```

---

## Environment Configuration

### Development

```bash
FLASK_ENV=development
FLASK_APP=run.py
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
HOST=localhost
PORT=5000
```

### Production

```bash
FLASK_ENV=production
FLASK_APP=run.py
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
HOST=0.0.0.0
PORT=5000
WORKERS=4
LOG_LEVEL=INFO
```

### Generate Secure Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Monitoring & Logging

### Container Logs

```bash
# View container logs
docker logs resume-builder

# Follow logs in real-time
docker logs -f resume-builder

# View logs from specific time
docker logs --since 2024-01-15 resume-builder
```

### Docker Compose Logs

```bash
# View all service logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100
```

### Health Checks

The application includes built-in health checks:

```bash
# Manual health check
curl http://localhost:5000/

# Docker health status
docker inspect --format='{{.State.Health.Status}}' resume-builder
```

### Log Aggregation (Optional)

For production, consider:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Datadog**
- **New Relic**
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

---

## Scaling

### Horizontal Scaling with Docker

```bash
# Run multiple instances with load balancing
docker run -d -p 5001:5000 --name resume-builder-1 resume-builder:latest
docker run -d -p 5002:5000 --name resume-builder-2 resume-builder:latest
docker run -d -p 5003:5000 --name resume-builder-3 resume-builder:latest

# Use Nginx as load balancer (see configuration above)
```

### Kubernetes Deployment (Advanced)

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resume-builder
spec:
  replicas: 3
  selector:
    matchLabels:
      app: resume-builder
  template:
    metadata:
      labels:
        app: resume-builder
    spec:
      containers:
      - name: resume-builder
        image: resume-builder:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: resume-builder-service
spec:
  selector:
    app: resume-builder
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

Deploy:

```bash
kubectl apply -f k8s-deployment.yaml
kubectl get services
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
docker run -p 8000:5000 resume-builder:latest
```

#### 2. Permission Denied (uploads)

```bash
# Fix uploads directory permissions
docker exec resume-builder chmod 755 /app/uploads

# Or in docker-compose
docker-compose exec web chmod 755 /app/uploads
```

#### 3. Out of Memory

```bash
# Limit container memory
docker run -m 512m -p 5000:5000 resume-builder:latest

# Check memory usage
docker stats resume-builder
```

#### 4. PDF Generation Fails

```bash
# Ensure wkhtmltopdf is installed
# The Dockerfile includes it, but verify:
docker exec resume-builder which wkhtmltopdf

# Install if missing
docker exec resume-builder apt-get update && apt-get install -y wkhtmltopdf
```

#### 5. Database Connection Issues

```bash
# Test database connection
docker-compose exec web python -c "import sqlite3; sqlite3.connect('/app/uploads/app.db').close()"
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export FLASK_ENV=development
export FLASK_DEBUG=1

# Or in docker-compose.yml
environment:
  - FLASK_ENV=development
  - FLASK_DEBUG=1
```

### View Container Details

```bash
# Inspect container
docker inspect resume-builder

# View resource usage
docker stats resume-builder

# View running processes
docker top resume-builder

# Access container shell
docker exec -it resume-builder bash
```

---

## Security Best Practices

1. **Never commit secrets** - Use GitHub Secrets and environment variables
2. **Use secret management** - Consider tools like Vault, AWS Secrets Manager
3. **Enable HTTPS** - Use Let's Encrypt for SSL certificates
4. **Keep dependencies updated** - Run security scans regularly
5. **Use strong SECRET_KEY** - Generate with `secrets.token_urlsafe(32)`
6. **Limit upload sizes** - MAX_CONTENT_LENGTH in config
7. **Validate input** - Sanitize user inputs
8. **Regular backups** - Backup uploads directory and data
9. **Monitor logs** - Set up log aggregation and alerting
10. **Rate limiting** - Consider adding rate limiting middleware

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OWASP Security Guidelines](https://owasp.org/)
- [Container Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Container_Security_Cheat_Sheet.html)

---

## Support & Contributing

For issues, questions, or contributions:

1. Check existing [GitHub Issues](https://github.com/yourusername/resume-builder/issues)
2. Create new issue with detailed description
3. Submit pull requests with improvements
4. Follow contribution guidelines in CONTRIBUTING.md

---

**Last Updated**: January 2024
