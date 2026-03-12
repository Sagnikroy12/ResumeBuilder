import os
from flask import Flask
from .models import User, Resume
from .routes.resume_routes import resume_bp
from .config.config import get_config
from .extensions import db, login_manager, bcrypt, migrate

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    
    config = get_config(config_name)
    app.config.from_object(config)
    
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
    app.register_blueprint(resume_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    
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
    
    return app