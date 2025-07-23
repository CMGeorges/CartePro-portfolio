# tests/test_admin.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def admin_user(client):
    with client.application.app_context():
        user = User(
            username="admin",
            email="admin@mail.com",
            password_hash=generate_password_hash("adminpass"),
            role="admin"
        )
        #db.set_password("adminpass")
        db.session.add(user)
        db.session.commit()
        return user

def login(client, username, password):
    return client.post('/auth/login', json={
        'username': username,
        'password': password
    })

def test_admin_routes(client, admin_user):
    # Connexion de l'utilisateur admin
    rv = login(client, "admin", "adminpass")
    assert rv.status_code == 200
    assert "Login" in rv.get_json()["message"]

    # Test route: /admin/users
    rv = client.get('/api/v1/admin/users')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

    # Test route: /admin/cards
    rv = client.get('/api/v1/admin/cards')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)

    # Test route: /admin/backups
    rv = client.get('/api/v1/admin/backups')
    assert rv.status_code == 200
    assert isinstance(rv.get_json(), list)
