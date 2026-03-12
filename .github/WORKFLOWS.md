# CI/CD Pipeline Documentation

This document describes the continuous integration and continuous deployment (CI/CD) pipeline for the Resume Builder application.

## Pipeline Architecture

```
Push to GitHub
    ↓
├─→ Tests (tests.yml)
│   ├─ Lint with flake8
│   ├─ Format check with black
│   ├─ Run pytest with coverage
│   └─ Upload coverage to Codecov
│
├─→ Build Docker (docker.yml)
│   ├─ Build multi-stage Docker image
│   ├─ Push to Docker Hub
│   └─ Push to GitHub Container Registry
│
├─→ Security Scan (security.yml)
│   ├─ Bandit: Python security checks
│   ├─ Safety: Dependency vulnerabilities
│   └─ Trivy: Container image scan
│
└─→ Code Quality (quality.yml)
    ├─ Pylint: Code analysis
    ├─ Radon: Complexity metrics
    └─ Generate reports
```

## Workflow Files

### 1. tests.yml - Test Pipeline

**Triggers:**
- Push to `main` or `develop` branch
- Pull requests to `main` or `develop` branch

**Matrix Testing:**
- Python 3.9, 3.10, 3.11

**Steps:**
1. Checkout code
2. Set up Python
3. Cache pip packages
4. Install dependencies
5. Lint with flake8
6. Format check with black
7. Run tests with pytest
8. Generate coverage reports
9. Upload to Codecov

**Success Criteria:**
- All tests pass
- Code coverage maintained
- No linting errors (critical)

### 2. docker.yml - Docker Build & Push

**Triggers:**
- Push to `main` or `develop` branch
- Tags matching `v*`
- Pull requests (build only, no push)

**Registry Targets:**
- Docker Hub: `${{ secrets.DOCKER_USERNAME }}/resume-builder`
- GitHub Container Registry: `ghcr.io/${{ github.repository }}`

**Tags Generated:**
- Branch: `develop`, `main`
- Semantic version: `v1.0.0` → `1.0.0`, `1.0`, `latest`
- Commit SHA: `main-abc123def456...`
- Latest: On default branch push

**Optimization:**
- Multi-stage Dockerfile
- GitHub Actions cache
- Layer caching between builds

### 3. security.yml - Security Scanning

**Triggers:**
- Push to `main` or `develop` branch
- All pull requests
- Daily schedule (2 AM UTC)

**Security Checks:**
- **Bandit**: Python security linting
- **Safety**: Vulnerable dependencies
- **Trivy**: Container image vulnerabilities

**Artifacts:**
- Bandit JSON report
- SARIF results (GitHub Security tab)

### 4. quality.yml - Code Quality

**Triggers:**
- Push to `main` or `develop` branch
- All pull requests

**Quality Metrics:**
- **Pylint**: Code quality score
- **Radon**: Complexity analysis
  - Cyclomatic complexity (A-F scale)
  - Maintainability index
  - Raw metrics

**Reports Generated:**
- `complexity.json`
- `metrics.json`

**Optional Integration:**
- SonarCloud (uncomment in workflow)

### 5. deploy.yml - Production Deployment

**Triggers:**
- Push to `main` branch
- Tags matching `v*`
- Manual trigger (`workflow_dispatch`)

**Environment:**
- Deployment environment protection
- Requires approval (if configured)

**Deployment Steps:**
1. Trigger tests
2. Deploy to production server
3. Health check
4. Slack notification

**Configuration Required:**
- Deployment server setup
- Deploy key in GitHub Secrets
- Slack webhook URL

---

## Setup Instructions

### 1. GitHub Secrets Configuration

Navigate to: `Settings → Secrets and variables → Actions`

Required secrets:

```
DOCKER_USERNAME
  └─ Your Docker Hub username
  
DOCKER_PASSWORD
  └─ Docker Hub personal access token (NOT password)
  
SLACK_WEBHOOK_URL (optional)
  └─ Slack incoming webhook for notifications
  
DEPLOY_KEY (optional)
  └─ SSH private key for deployment server
```

### 2. Branch Protection Rules

Configure in: `Settings → Branches → Add rule`

Example for `main` branch:

```
Pattern name: main
  ✓ Require a pull request before merging
  ✓ Require status checks to pass before merging
    - Tests (tests.yml)
    - Build and Push Docker Image (docker.yml)
  ✓ Require branches to be up to date before merging
  ✓ Require code reviews before merging (recommended: 1)
  ✓ Dismiss stale pull request approvals
  ✓ Require status checks from protected branches
```

### 3. Docker Hub Setup

1. Create Docker Hub account (free tier available)
2. Create personal access token:
   - Login to Docker Hub
   - Account Settings → Security → New Access Token
   - Copy token and add to GitHub Secrets as `DOCKER_PASSWORD`

### 4. GitHub Container Registry Setup

No additional setup needed - uses `GITHUB_TOKEN` automatically.

### 5. Codecov Integration (Optional)

1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Enable repository
4. Workflow will automatically upload coverage reports

---

## Running Workflows Locally

### Test Workflow Locally with act

```bash
# Install act (GitHub Actions local runner)
# macOS: brew install act
# Windows: choco install act-cli
# Linux: Follow installation guide

# Run tests workflow locally
act push --file .github/workflows/tests.yml

# Run with specific event
act pull_request --file .github/workflows/tests.yml

# View available events
act --list
```

### Manual Workflow Trigger

```bash
# Using GitHub CLI
gh workflow run tests.yml
gh workflow run docker.yml
gh workflow run deploy.yml

# Monitor workflow execution
gh run list
gh run view <RUN_ID> --log
```

---

## Monitoring Workflows

### GitHub Actions Interface

1. Go to `Actions` tab in repository
2. Select workflow from left sidebar
3. Click run to view details:
   - Status (success/failure)
   - Execution time
   - Job logs
   - Artifacts

### Workflow Status Badge

Add to README.md:

```markdown
![Tests](https://github.com/yourusername/resume-builder/actions/workflows/tests.yml/badge.svg)
![Docker](https://github.com/yourusername/resume-builder/actions/workflows/docker.yml/badge.svg)
![Security](https://github.com/yourusername/resume-builder/actions/workflows/security.yml/badge.svg)
```

### Email Notifications

Configure in GitHub:
- Settings → Notifications
- Choose notification preferences
- Enable workflow notifications

---

## Troubleshooting

### Workflow Failures

**Tests Failing:**
```bash
# Run tests locally
pytest tests/ -v

# Check Python version compatibility
python --version

# View specific test failure
pytest tests/test_routes.py::TestResumeRoutes::test_index_get_request -v
```

**Docker Build Failing:**
```bash
# Build locally
docker build -t resume-builder:latest .

# Check Dockerfile
docker build --no-cache -t resume-builder:latest .

# View layer by layer
docker build --progress=plain -t resume-builder:latest .
```

**Push to Registry Failing:**
```bash
# Verify secrets
gh secret list

# Test Docker Hub login
echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin

# Check registry connectivity
docker pull docker.io/library/python:3.11-slim
```

### Workflow Timeout

- Default: 6 hours per job
- Can be extended in workflow settings
- Consider splitting large jobs

### Secrets Not Available

- Check secret names match exactly
- Ensure secret value is not empty
- Secrets are not logged in workflow output

### Caching Issues

Clear cache:
```bash
gh actions-cache delete --pattern 'coverage-*' --all
gh actions-cache delete --pattern 'pip-*' --all
```

---

## Performance Optimization

### Speed Up Tests

```yaml
# Parallel test execution
pytest tests/ -n auto

# Run only changed files
pytest --lf  # Last failed
pytest --ff  # Failed first
```

### Docker Build Caching

```dockerfile
# Good - cache layers by frequency
RUN apt-get update && apt-get install -y python3
COPY requirements.txt .
RUN pip install -r requirements.txt  # Large, changes infrequently
COPY . .  # Small, changes frequently
```

### GitHub Actions Caching

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

---

## Best Practices

1. **Keep workflows DRY** - Use composite actions for reusable steps
2. **Fail fast** - Order jobs by likelihood of failure
3. **Version dependencies** - Pin versions in requirements.txt
4. **Security**:
   - Rotate secrets regularly
   - Use fine-grained tokens
   - Don't commit credentials
5. **Logging**:
   - Use `::debug::` for debug messages
   - `::notice::` for important info
   - `::warning::` and `::error::` for issues
6. **Documentation** - Keep workflows well-commented
7. **Testing**:
   - Test workflow files locally with `act`
   - Create test branches before pushing
   - Review workflow changes in PRs

---

## Cost Optimization

**GitHub Actions Free Tier:**
- 2,000 minutes/month for private repos
- Unlimited for public repos

**Optimize usage:**
```yaml
# Run on main/develop only, not every branch
on:
  push:
    branches: [ main, develop ]
    
# Skip expensive workflows on non-code changes
jobs:
  skip-redundant:
    runs-on: ubuntu-latest
    if: |
      !contains(github.event.head_commit.message, '[skip ci]')
```

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Runner Image Specifications](https://github.com/actions/runner-images)

---

**Last Updated**: January 2024
