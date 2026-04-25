# 🚀 AI-Powered Resume Builder — Backend API

> **A full-stack SaaS application that uses AI to help users build professional, ATS-optimized resumes in seconds.**

🌐 **Live App**: [aipoweredresumebuilder.netlify.app](https://aipoweredresumebuilder.netlify.app)  
🔗 **Frontend Repo**: [ResumeBuilder-Frontend](https://github.com/Sagnikroy12/ResumeBuilder-Frontend)  
⚙️ **Backend API**: [smartresumebuilder.onrender.com](https://smartresumebuilder.onrender.com)

---

## ✨ Features

- 🤖 **AI-Powered Content Generation** — Leverages Google Gemini, OpenAI, Anthropic Claude, and DeepSeek APIs to generate tailored resume content
- 📄 **Multiple Professional Templates** — Classic, Modern, and ATS-optimized designs
- 📊 **Live Preview** — Real-time resume rendering as you type
- 📥 **PDF Export** — One-click professional PDF generation
- 🔐 **User Authentication** — Secure login/registration with session management
- 💎 **Premium Tier** — Pro features with tiered access control
- 🐳 **Dockerized** — Fully containerized for reproducible deployments
- 🔄 **CI/CD Pipeline** — Automated testing via GitHub Actions
- 🏥 **Production Health Monitoring** — Built-in health check endpoint for uptime monitoring

---

## 🏗️ Architecture

This project follows a **decoupled frontend-backend architecture**:

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│   React Frontend    │  REST   │   Flask Backend      │  SQL    │   PostgreSQL    │
│   (Netlify)         │ ◄─────► │   (Render)           │ ◄─────► │   (Supabase)    │
└─────────────────────┘         └─────────────────────┘         └─────────────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │   AI Services   │
                                │  Gemini/OpenAI  │
                                │  Claude/DeepSeek│
                                └─────────────────┘
```

| Layer       | Technology                          | Hosting       |
|-------------|-------------------------------------|---------------|
| Frontend    | React, Vite, JavaScript             | Netlify       |
| Backend API | Flask, Gunicorn, Python             | Render        |
| Database    | PostgreSQL                          | Supabase      |
| AI Services | Gemini, OpenAI, Claude, DeepSeek    | External APIs |

---

## 🛠️ Tech Stack

### Backend (This Repo)
- **Framework**: Flask 2.3 with Application Factory pattern
- **Auth**: Flask-Login with Bcrypt password hashing
- **ORM**: Flask-SQLAlchemy + Flask-Migrate (Alembic)
- **Database**: PostgreSQL (Supabase) — with SQLite fallback for local dev
- **AI Integration**: Multi-provider support (Gemini, OpenAI, Claude, DeepSeek, Cerebras, SambaNova)
- **PDF Generation**: ReportLab + wkhtmltopdf
- **Security**: CORS, secure session cookies, environment-based config
- **Deployment**: Docker, Gunicorn, Render

### Frontend ([View Repo](https://github.com/Sagnikroy12/ResumeBuilder-Frontend))
- **Framework**: React + Vite
- **Styling**: Modern CSS with responsive design
- **Hosting**: Netlify with continuous deployment

---

## 📁 Project Structure

```
ResumeBuilder/
├── app/                          # Flask application
│   ├── __init__.py              # App factory with production guards
│   ├── config/                  # Environment-based configuration
│   ├── models/                  # SQLAlchemy data models
│   ├── routes/                  # API endpoints & blueprints
│   │   ├── auth_routes.py       # Authentication (login/register/logout)
│   │   ├── resume_routes.py     # Resume CRUD & AI generation
│   │   ├── dashboard_routes.py  # User dashboard
│   │   └── health_routes.py     # Production health check
│   ├── services/                # Business logic & AI integrations
│   └── utils/                   # Shared utilities
├── docs/                         # Extended documentation
├── tests/                        # Automated test suite
├── Dockerfile                   # Production container
├── docker-compose.yml           # Multi-service orchestration
├── requirements.txt             # Python dependencies
└── run.py                       # Application entry point
```

---

## 🚀 Quick Start

### Local Development

```bash
# Clone
git clone https://github.com/Sagnikroy12/ResumeBuilder.git
cd ResumeBuilder

# Setup
python -m venv venv
.\venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Configure Environment
cp .env.example .env           # Edit with your API keys
# IMPORTANT: You must export the following env vars or set them in .env:
# FLASK_ENV=development
# SECRET_KEY=your-secret-key
# DATABASE_URL=postgresql://user:pass@host:5432/dbname (or sqlite will be used locally)

# Initialize / Reset Database (If you encounter login/register schemas errors)
flask db upgrade               # Apply migrations
# OR to completely reset tables (Warning: Drops all data):
# python scripts/reset_remote_db.py

# Run (branch-aware env)
python scripts/run-backend-branch.py   # http://localhost:5000
# Fallback direct run:
# python run.py
```

### Docker

```bash
docker-compose up -d           # http://localhost:5000
```

---

## 🔑 API Endpoints

| Method | Endpoint              | Description                   | Auth Required |
|--------|-----------------------|-------------------------------|---------------|
| POST   | `/auth/register`      | Create new user account       | No            |
| POST   | `/auth/login`         | Authenticate user             | No            |
| POST   | `/auth/logout`        | End user session              | Yes           |
| GET    | `/auth/me`            | Get current user profile      | No            |
| GET    | `/resumes`            | List user's saved resumes     | Yes           |
| POST   | `/resumes`            | Create/save a resume          | Yes           |
| GET    | `/resumes/<id>`       | Get specific resume           | Yes           |
| DELETE | `/resumes/<id>`       | Delete a resume               | Yes           |
| POST   | `/resumes/ai`         | AI-powered content generation | Yes           |
| GET    | `/health`             | Health check for monitoring   | No            |

---

## 🧪 Testing

```bash
pytest tests/                              # Run all tests
pytest tests/ --cov=app --cov-report=html  # With coverage
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

## 👤 Author

**Sagnik Roy**  
📧 sagnikroyofficial24@gmail.com  
🔗 [GitHub](https://github.com/Sagnikroy12)

---

**Status**: Production Ready ✅ · **Version**: 1.0.0 · **Last Updated**: April 2026

### Environment & Migrations

- Required env vars:
  - SECRET_KEY - Flask session secret
  - DATABASE_URL - SQLAlchemy database URL (example: postgresql://user:pass@host:5432/dbname)

- Applying migrations (if using Flask-Migrate):
  1. pip install -r requirements.txt
  2. export FLASK_APP=run.py
  3. flask db upgrade

- Quick dev fallback: the app will fallback to a local SQLite `app.db` if DATABASE_URL is unset.