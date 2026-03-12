#!/bin/bash
# Quick Reference Commands for Resume Builder

echo "=========================================="
echo "Resume Builder - Quick Reference"
echo "=========================================="

# DEVELOPMENT
echo ""
echo "--- DEVELOPMENT ---"
echo "python -m venv venv              # Create virtual environment"
echo "source venv/bin/activate          # Activate virtual environment (Linux/macOS)"
echo "pip install -r requirements.txt   # Install dependencies"
echo "python run.py                     # Run locally"
echo "pytest tests/                     # Run tests"
echo "black app tests                   # Format code"
echo "flake8 app tests                  # Check code style"

# DOCKER
echo ""
echo "--- DOCKER ---"
echo "docker build -t resume-builder:latest .           # Build image"
echo "docker run -p 5000:5000 resume-builder:latest     # Run container"
echo "docker-compose up -d                              # Start with compose"
echo "docker-compose down                               # Stop services"
echo "docker-compose logs -f web                        # View logs"
echo "docker-compose exec web pytest tests/             # Run tests in container"

# GIT
echo ""
echo "--- GIT ---"
echo "git checkout -b feature/name                      # Create feature branch"
echo "git add .                                         # Stage changes"
echo "git commit -m 'feat: description'                 # Commit changes"
echo "git push origin feature/name                      # Push to fork"

# TESTING
echo ""
echo "--- TESTING ---"
echo "pytest tests/ -v                                  # Run tests verbose"
echo "pytest tests/ --cov=app                           # Run with coverage"
echo "pytest tests/ --cov=app --cov-report=html         # Generate HTML report"
echo "pytest tests/test_routes.py -v                    # Run specific test file"
echo "pytest -k test_index                              # Run tests by pattern"

# CODE QUALITY
echo ""
echo "--- CODE QUALITY ---"
echo "black app tests                   # Auto-format code"
echo "flake8 app tests                  # Check style issues"
echo "isort app tests                   # Sort imports"
echo "pylint app                        # Run linter"
echo "bandit -r app                     # Security check"
echo "safety check                      # Check dependencies"

# UTILITIES
echo ""
echo "--- USEFUL UTILITIES ---"
echo "docker ps                         # List running containers"
echo "docker logs <container>           # View container logs"
echo "docker exec -it <container> bash  # Access container shell"
echo "git status                        # Check git status"
echo "git log --oneline                 # View commit history"

echo ""
echo "=========================================="
echo "For more info, see:"
echo "  README.md - Project overview"
echo "  DEPLOYMENT.md - Deployment guide"
echo "  CONTRIBUTING.md - Contributing guide"
echo "  .github/WORKFLOWS.md - CI/CD documentation"
echo "=========================================="
