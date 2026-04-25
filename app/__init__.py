import os
from flask import Flask
from .models import User, Resume
from .routes.resume_routes import resume_bp
from .config.config import get_config
from .extensions import db, login_manager, bcrypt
from flask_cors import CORS

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)
    # Load configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    
    config = get_config(config_name)
    app.config.from_object(config)
    
    # CORS configuration - MUST be after config is loaded
    default_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    allowed_origins = app.config.get('ALLOWED_ORIGINS', default_origins)
    CORS(app, supports_credentials=True, origins=allowed_origins)
    
    # Session cookie policy must vary by environment:
    # - Local/dev (HTTP): SameSite=None + Secure=True works on localhost in most browsers
    # - Production cross-site auth (HTTPS): SameSite=None + Secure=True
    is_production = app.config.get("FLASK_ENV") == "production"
    
    app.config.update(
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True, # Modern browsers allow Secure cookies on localhost over HTTP
        SESSION_COOKIE_HTTPONLY=True,
    )
    
    from .extensions import db, login_manager, bcrypt, migrate
    
    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    # Ensure upload folder exists
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)
    
    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.dashboard_routes import dashboard_bp
    from .routes.debug_routes import debug_bp
    from .routes.health_routes import health_bp
    app.register_blueprint(resume_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(health_bp)
    
    # Only register debug routes if app is in debug mode
    if app.debug:
        app.register_blueprint(debug_bp)
    
    # Create database tables within app context
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created/verified successfully.")
        except Exception as e:
            app.logger.error(f"Error during db.create_all(): {str(e)}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {"error": "File too large"}, 413
    
    # Custom Jinja Filters
    from .services.resume_service import ResumeService
    from .utils.text_utils import parse_bullets

    @app.template_filter('format_bullets')
    def format_bullets_filter(value):
        if not value:
            return ""
        if isinstance(value, str):
            bullets = parse_bullets(value)
        elif isinstance(value, list):
            bullets = value
        else:
            bullets = [str(value)]
        return ResumeService.to_li(bullets)
    
    return app