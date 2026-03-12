"""
Tests for application configuration
"""

import pytest
from app.config.config import get_config, Config, DevelopmentConfig, TestingConfig, ProductionConfig


class TestConfiguration:
    """Test cases for configuration management"""
    
    def test_get_default_config(self):
        """Test getting default configuration"""
        config = get_config()
        assert config is not None
    
    def test_get_development_config(self):
        """Test getting development configuration"""
        config = get_config("development")
        assert config == DevelopmentConfig
        assert DevelopmentConfig.DEBUG is True
        assert DevelopmentConfig.TESTING is False
    
    def test_get_testing_config(self):
        """Test getting testing configuration"""
        config = get_config("testing")
        assert config == TestingConfig
        assert TestingConfig.DEBUG is True
        assert TestingConfig.TESTING is True
    
    def test_get_production_config(self):
        """Test getting production configuration"""
        config = get_config("production")
        assert config == ProductionConfig
        assert ProductionConfig.DEBUG is False
        assert ProductionConfig.TESTING is False
    
    def test_production_config_security_settings(self):
        """Test production config has security settings"""
        assert ProductionConfig.SESSION_COOKIE_SECURE is True
        assert ProductionConfig.SESSION_COOKIE_HTTPONLY is True
        assert ProductionConfig.SESSION_COOKIE_SAMESITE == 'Lax'
    
    def test_config_has_required_attributes(self):
        """Test config has all required attributes"""
        config = get_config()
        assert hasattr(config, "SECRET_KEY")
        assert hasattr(config, "DEBUG")
        assert hasattr(config, "TESTING")
        assert hasattr(config, "UPLOAD_FOLDER")
        assert hasattr(config, "MAX_CONTENT_LENGTH")
    
    def test_config_max_content_length(self):
        """Test max content length is set"""
        config = Config()
        assert config.MAX_CONTENT_LENGTH > 0
    
    def test_config_allowed_extensions(self):
        """Test allowed extensions are configured"""
        config = Config()
        assert 'pdf' in config.ALLOWED_EXTENSIONS
        assert 'txt' in config.ALLOWED_EXTENSIONS
