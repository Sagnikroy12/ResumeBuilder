"""
Configuration Management for Resume Builder Application
Supports development, testing, and production environments
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = False
    TESTING = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_SIZE", 50000000))  # 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
    
    # Database Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Heroku and Render sometimes use 'postgres://' which SQLAlchemy 1.4+ deprecated in favor of 'postgresql://'
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or \
        'sqlite:///' + os.path.join(basedir, '..', '..', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    # API Configuration
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    
    # Session Refresh
    SESSION_REFRESH_EACH_REQUEST = True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    FLASK_ENV = "development"
    # Ensure local development always uses local SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Config.basedir, '..', '..', 'app.db')

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    FLASK_ENV = "testing"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    FLASK_ENV = "production"
    
    # Enforce secure settings in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Add explicit check for DATABASE_URL in production
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        import logging
        logging.critical("DATABASE_URL is not set in production! Falling back to local SQLite 'app.db' which is EPHEMERAL on Render.")
    
    # In production, we should be more specific about origins
    # This will be overridden by environment variable if set

class StagingConfig(ProductionConfig):
    """Staging configuration - similar to production with some debugging"""
    DEBUG = False

# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "staging": StagingConfig,
    "default": DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration object based on environment"""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    return config.get(config_name, config["default"])
