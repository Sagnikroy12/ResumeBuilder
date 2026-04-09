import pytest
from app.models.user import User
from app.extensions import db

def test_user_registration(client, app):
    """Test user registration"""
    with app.app_context():
        # Clear existing users
        db.session.query(User).delete()
        db.session.commit()

    response = client.post('/auth/register', json={
        'email': 'testing@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 201
    
    with app.app_context():
        user = User.query.filter_by(email='testing@example.com').first()
        assert user is not None
        assert user.check_password('password123')

def test_duplicate_registration_returns_409(client, app):
    """Test duplicate user registration"""
    with app.app_context():
        # Clear existing users
        db.session.query(User).delete()
        db.session.commit()

    # First registration
    client.post('/auth/register', json={
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    
    # Second registration should fail with 409
    response = client.post('/auth/register', json={
        'email': 'duplicate@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 409
    
def test_user_login(client, app):
    """Test user login"""
    with app.app_context():
        db.session.query(User).delete()
        db.session.commit()

    # Register
    client.post('/auth/register', json={
        'email': 'login_test@example.com',
        'password': 'password123'
    })
    
    # Login
    response = client.post('/auth/login', json={
        'email': 'login_test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['user']['email'] == 'login_test@example.com'