"""
Test configuration and fixtures
"""

import pytest
import os
import tempfile
from app import create_app

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app("testing")
    
    # Create temporary directory for uploads
    with tempfile.TemporaryDirectory() as tmpdir:
        app.config["UPLOAD_FOLDER"] = tmpdir
        yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()
