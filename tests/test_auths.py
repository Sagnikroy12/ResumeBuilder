import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_register_and_login(client):
    resp = client.post("/auth/register", json={"email":"u1@example.com","password":"Password123"})
    assert resp.status_code == 201

    resp = client.post("/auth/login", json={"email":"u1@example.com","password":"Password123"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data and data.get("status") == "success"