# Contributing to Resume Builder

Thank you for your interest in contributing to the Resume Builder project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help new contributors
- Respect differing opinions

## Getting Started

### 1. Fork and Clone

```bash
# Fork repository on GitHub
# then clone your fork
git clone https://github.com/YOUR-USERNAME/resume-builder.git
cd resume-builder

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/resume-builder.git
```

### 2. Create Feature Branch

```bash
# Update from original repository
git fetch upstream
git checkout develop

# Create feature branch
git checkout -b feature/your-feature-name
```

### 3. Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## Development Workflow

### 1. Make Changes

Create/modify files according to project structure:

```
app/
├── config/       - Configuration files
├── routes/       - API endpoints and views
├── services/     - Business logic
├── utils/        - Helper functions
├── static/       - CSS, JS, images
└── templates/    - HTML templates
```

### 2. Run Tests Locally

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_routes.py::TestResumeRoutes::test_index_post_request_with_basic_data -v

# Run in watch mode
pytest-watch tests/
```

### 3. Code Quality Checks

```bash
# Format with black
black app tests

# Check with flake8
flake8 app tests

# Sort imports
isort app tests

# Lint with pylint
pylint app --disable=C0111

# Check security
bandit -r app

# Check vulnerabilities
safety check
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "feat: Add new resume template"

# Commit types: feat, fix, docs, style, refactor, test, chore
```

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# - Use clear title and description
# - Reference issues if applicable
# - Link to related PRs
```

## Pull Request Guidelines

### PR Title Format

```
[TYPE] Short description

Types: feat, fix, docs, style, refactor, test, chore
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Code refactoring
- [ ] Performance improvement

## Related Issues
Fixes #123
Related to #456

## Testing
- [ ] Unit tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Comments added for complex logic
- [ ] Tests updated
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. At least 1 maintainer review required
2. All CI/CD checks must pass
3. Code coverage maintained or improved
4. No merge conflicts
5. Branch up to date with main

## Coding Standards

### Python Style

- Follow PEP 8
- Line length: 100-120 characters (soft limit)
- Use type hints where appropriate
- Document functions with docstrings

**Example:**

```python
def parse_resume_data(raw_data: dict) -> dict:
    """
    Parse and validate resume data.
    
    Args:
        raw_data: Raw form submission data
        
    Returns:
        Validated and formatted resume data
        
    Raises:
        ValueError: If validation fails
    """
    # Implementation
    return processed_data
```

### HTML/CSS/JavaScript

- Use semantic HTML5
- CSS classes use kebab-case
- JavaScript uses camelCase
- Responsive design (mobile-first)
- WCAG 2.1 accessibility compliance

### Commit Messages

```
Type: Description

[BODY - Optional detailed explanation]

[FOOTER - Optional reference to issues]

Example:
feat: Add dark mode support

Add dark mode toggle in settings menu.
Implement CSS variables for theme switching.

Fixes #234
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code structure changes
- `test`: Adding or updating tests
- `chore`: Dependency updates, config changes

## Testing Requirements

All PRs must include:

1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test component interactions
3. **Coverage** - Minimum 80% code coverage

```bash
# Run coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Documentation

Update documentation for:

- New features
- API changes
- Configuration options
- Deployment procedures
- Breaking changes

Files to update:
- `README.md` - Feature overview
- `DEPLOYMENT.md` - Deployment details
- `.github/WORKFLOWS.md` - CI/CD changes
- Code comments - Complex logic
- Docstrings - Function documentation

## Issue Guidelines

### Reporting Bugs

**Title**: `[BUG] Descriptive title`

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 10
- Python: 3.10
- Docker: 20.10

## Screenshots
[If applicable]
```

### Requesting Features

**Title**: `[FEATURE] Descriptive title`

```markdown
## Description
Clear description of requested feature

## Use Case
Why this feature is needed

## Proposed Solution
How the feature should work

## Alternatives Considered
Other approaches

## Additional Context
Any other information
```

## Review Checklist for Maintainers

- [ ] Follows coding standards
- [ ] Includes appropriate tests
- [ ] Documentation is updated
- [ ] Changes are backwards compatible
- [ ] All CI/CD checks pass
- [ ] No security vulnerabilities
- [ ] Performance impact minimal
- [ ] Code is well-commented
- [ ] Commit messages are clear

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release PR to main branch
4. After merge, create GitHub Release
5. Docker image auto-pushed to registries
6. Create release notes

## Getting Help

- 📖 Check [DEPLOYMENT.md](DEPLOYMENT.md)
- 🔍 Search existing [Issues](https://github.com/yourusername/resume-builder/issues)
- 💬 Start [Discussion](https://github.com/yourusername/resume-builder/discussions)
- 📧 Email maintainers

## Acknowledgements

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Credited in project documentation

## Questions?

- Open a Discussion
- Comment on related Issue
- Start an Issue with [QUESTION] prefix

---

Thank you for contributing! Your work helps make Resume Builder better for everyone. 🙏
