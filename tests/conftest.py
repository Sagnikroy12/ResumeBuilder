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
        with app.app_context():
            from app.extensions import db
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_client(app):
    from app.models.user import User
    from app.extensions import db, bcrypt
    client = app.test_client()
    with app.app_context():
        pw = bcrypt.generate_password_hash("testpass").decode('utf-8')
        user = User(username="testuser", email="test@test.com", password_hash=pw)
        db.session.add(user)
        db.session.commit()
    
    client.post('/auth/login', data={'email': 'test@test.com', 'password': 'testpass', 'remember': 'on'})
    return client

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()
