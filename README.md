# Resume Builder - SaaS Application

A modern, containerized resume/CV builder web application built with Flask. Generate professional resumes in multiple templates with PDF export functionality.

![Tests](https://github.com/yourusername/resume-builder/actions/workflows/tests.yml/badge.svg)
![Docker](https://github.com/yourusername/resume-builder/actions/workflows/docker.yml/badge.svg)
![Security](https://github.com/yourusername/resume-builder/actions/workflows/security.yml/badge.svg)

## Features

- ✅ **Multiple Templates** - Choose from Classic, Modern, and Professional resume designs
- ✅ **Live Preview** - Real-time resume preview as you type
- ✅ **PDF Export** - Generate professional PDF resumes
- ✅ **Responsive Design** - Works on desktop and mobile devices
- ✅ **Docker Ready** - Containerized for easy deployment
- ✅ **CI/CD Pipeline** - Automated testing, building, and deployment with GitHub Actions
- ✅ **Production Ready** - Environment-based configuration, security best practices
- ✅ **Comprehensive Tests** - Unit and integration tests with >80% coverage
- ✅ **Security Scanning** - Automated vulnerability detection

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder

# Start with Docker Compose
docker-compose up -d

# Application will be available at http://localhost:5000
```

### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run application
python run.py

# Application will be available at http://localhost:5000
```

## Prerequisites

### For Docker
- Docker Desktop (v20.10+)
- Docker Compose (v1.29+)

### For Local Development
- Python 3.9+
- pip (Python package manager)
- wkhtmltopdf (for PDF generation)

### Install wkhtmltopdf

**Windows:**
- Download from https://wkhtmltopdf.org/downloads.html
- Run installer
- Update path in `app/services/pdf_service.py` if needed

**macOS:**
```bash
brew install --cask wkhtmltopdf
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install wkhtmltopdf
```

## Project Structure

```
resume-builder/
├── app/                          # Flask application package
│   ├── __init__.py              # App factory
│   ├── config/
│   │   ├── config.py            # Configuration management
│   │   └── templates_config.py  # Template registry
│   ├── routes/
│   │   └── resume_routes.py     # Resume endpoints
│   ├── services/
│   │   └── pdf_service.py       # PDF generation
│   ├── utils/
│   │   └── text_utils.py        # Utility functions
│   ├── static/                  # CSS, JavaScript files
│   └── templates/               # HTML templates
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest configuration
│   ├── test_routes.py           # Route tests
│   ├── test_config.py           # Configuration tests
│   ├── test_utils.py            # Utility function tests
│   └── test_services.py         # Service tests
├── .github/
│   ├── workflows/               # GitHub Actions workflows
│   │   ├── tests.yml           # Test pipeline
│   │   ├── docker.yml          # Docker build & push
│   │   ├── security.yml        # Security scanning
│   │   ├── quality.yml         # Code quality
│   │   └── deploy.yml          # Production deployment
│   └── WORKFLOWS.md            # CI/CD documentation
├── uploads/                     # Generated PDFs storage
├── Dockerfile                   # Container definition
├── docker-compose.yml          # Docker Compose configuration
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── run.py                      # Application entry point
├── DEPLOYMENT.md               # Deployment guide
└── README.md                   # This file
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_APP=run.py
DEBUG=False
SECRET_KEY=your-secret-key-here
PORT=5000

# Server Configuration
HOST=0.0.0.0
WORKERS=4

# File Upload
MAX_UPLOAD_SIZE=50000000
ALLOWED_EXTENSIONS=pdf,txt,doc,docx
```

See [.env.example](.env.example) for all available options.

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_routes.py -v

# Run tests continuously on file changes
pytest-watch tests/
```

### Code Quality

```bash
# Format code
black app tests

# Check code style
flake8 app tests

# Sort imports
isort app tests

# Lint code
pylint app

# Check security issues
bandit -r app

# Check dependencies for vulnerabilities
safety check
```

### Docker Development

```bash
# Build image
docker build -t resume-builder:latest .

# Run container
docker run -p 5000:5000 resume-builder:latest

# View logs
docker logs -f <container_id>

# Access container shell
docker exec -it <container_id> bash

# Run tests in container
docker-compose exec web pytest tests/
```

## Deployment

### Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including:

- Local development setup
- Docker setup and configuration
- GitHub Actions CI/CD pipeline
- Deployment to various platforms:
  - AWS ECS
  - Google Cloud Run
  - Heroku
  - Your own server
- Monitoring and logging
- Scaling strategies
- Troubleshooting guides

### Quick Deployment

#### AWS ECS
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag resume-builder:latest <account>.dkr.ecr.us-east-1.amazonaws.com/resume-builder:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/resume-builder:latest
```

#### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/resume-builder:latest
gcloud run deploy resume-builder --image gcr.io/PROJECT-ID/resume-builder:latest --platform managed --region us-central1
```

#### Heroku
```bash
heroku create your-app-name
heroku config:set FLASK_ENV=production
git push heroku main
```

## CI/CD Pipeline

### GitHub Actions Workflows

Automated workflows for testing, security, quality, and deployment:

1. **Tests** - Runs on every push/PR
   - Unit tests with pytest
   - Code coverage reporting
   - Linting and formatting checks

2. **Docker Build** - Builds and pushes Docker images
   - Multi-stage optimized builds
   - Auto-tagging based on branch/tag
   - Push to Docker Hub and GitHub Container Registry

3. **Security** - Security vulnerability scanning
   - Python security (Bandit)
   - Dependency vulnerabilities (Safety)
   - Container scanning (Trivy)

4. **Code Quality** - Code quality analysis
   - Complexity metrics (Radon)
   - Code analysis (Pylint)
   - Optional SonarCloud integration

5. **Deploy** - Production deployment
   - Automated deployment to production
   - Health checks
   - Slack notifications

See [.github/WORKFLOWS.md](.github/WORKFLOWS.md) for detailed CI/CD documentation.

### Setting Up GitHub Secrets

Add these secrets to GitHub repository (Settings → Secrets):

```
DOCKER_USERNAME     - Docker Hub username
DOCKER_PASSWORD     - Docker Hub personal access token
SLACK_WEBHOOK_URL   - Slack webhook for notifications (optional)
DEPLOY_KEY          - SSH key for deployment server (optional)
```

## API Endpoints

### GET / 
Display resume builder form

### POST /
Generate resume from form data

**Form Parameters:**
- `template` (string) - Template ID: template1, template2, or template3
- `name` (string) - Full name
- `email` (string) - Email address
- `phone` (string) - Phone number
- `address` (string) - Address
- `linkedin` (string) - LinkedIn URL
- `objective` (string) - Career objective
- `skills` (string) - Skills (one per line)
- `exp_title[]` (array) - Experience titles
- `exp_duration[]` (array) - Experience durations
- `exp_points[]` (array) - Experience responsibilities
- `projects` (string) - Projects (one per line)
- `education` (string) - Education information
- `certifications` (string) - Certifications (one per line)
- `section_title[]` (array) - Custom section titles
- `section_points[]` (array) - Custom section content

## Templates

### Template 1: Classic
Traditional resume format with 2-column skills layout

### Template 2: Modern
Contemporary design with clean typography

### Template 3: Professional
ATS-optimized professional format

## Technologies Used

- **Backend**: Flask 2.3+
- **PDF Generation**: reportlab, wkhtmltopdf
- **Frontend**: HTML, CSS, JavaScript
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, flake8, pylint, bandit
- **Deployment**: Gunicorn, Nginx

## System Requirements

### Minimum
- 512 MB RAM
- 100 MB disk space
- Python 3.9+

### Recommended
- 1+ GB RAM
- 1+ GB disk space
- Python 3.11
- Docker 20.10+

## Troubleshooting

### PDF Generation Issues
- Ensure wkhtmltopdf is installed and in PATH
- Check file permissions in uploads directory
- Verify adequate disk space

### Port Already in Use
```bash
# Find and kill process using port 5000
lsof -i :5000
kill -9 <PID>

# Or use different port
python run.py --port 8000
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version  # Should be 3.9+
```

### Docker Issues
```bash
# Rebuild without cache
docker-compose up -d --build --no-cache

# View logs
docker-compose logs -f web

# Reset volumes
docker-compose down -v
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for more troubleshooting guides.

## Performance Tips

1. **Use Docker** for consistent deployment
2. **Enable caching** in reverse proxy
3. **Optimize PDF generation** - Consider async processing for large batches
4. **Monitor resources** - Watch CPU and memory usage
5. **Use CDN** for static files in production
6. **Implement rate limiting** for API endpoints

## Security

- Environment-based configuration
- Secure secret management
- Input validation and sanitization
- CORS configuration
- Security headers
- Regular dependency updates
- Automated vulnerability scanning
- SSL/TLS support

See [DEPLOYMENT.md](DEPLOYMENT.md) for security best practices.

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Development Workflow

1. Create branch from `develop`
2. Make changes and test locally
3. Run full test suite: `pytest tests/`
4. Push to GitHub (triggers CI/CD)
5. Create Pull Request
6. Wait for all checks to pass
7. Request review
8. Merge after approval

## Roadmap

- [ ] Database integration (PostgreSQL)
- [ ] User authentication and profiles
- [ ] Resume templates library expansion
- [ ] Export formats (DOCX, HTML)
- [ ] Email resume delivery
- [ ] Resume analytics
- [ ] Collaboration features
- [ ] Mobile app
- [ ] AI-powered content suggestions

## License

MIT License - see LICENSE file for details

## Support

- 📧 Email: sagnikroyofficial24@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/resume-builder/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/resume-builder/discussions)
- 📚 Documentation: [DEPLOYMENT.md](DEPLOYMENT.md), [WORKFLOWS.md](.github/WORKFLOWS.md)

## Authors

- Your Name - Sagnik Roy

## Acknowledgments

- Flask documentation and community
- Bootstrap CSS framework
- reportlab PDF library
- All contributors and testers

---

**Version**: 1.0.0  
**Last Updated**: March 2026
**Status**: Production Ready ✅

