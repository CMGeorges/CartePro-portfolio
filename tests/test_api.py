import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def register(client, username, password):
    return client.post('/auth/register', json={'username': username, 'password': password})

def login(client, username, password):
    return client.post('/auth/login', json={'username': username, 'password': password})

def test_health(client):
    resp = client.get('/api/v1/')
    assert resp.status_code == 200
    assert resp.get_json()['message'] == 'QR Card API is running.'

def test_generate_qr(client):
    data = {'url': 'https://example.com'}
    resp = client.post('/api/v1/generate', json=data)
    assert resp.status_code == 200
    assert resp.mimetype == 'image/png'

def test_card_lifecycle(client):
    register(client, 'alice', 'pass')
    login(client, 'alice', 'pass')

    create_resp = client.post('/api/v1/cards', json={
        'name': 'Alice Card',
        'email': 'alice@example.com',
        'title': 'CEO'
    })
    assert create_resp.status_code == 201
    card_id = create_resp.get_json()['id']

    get_resp = client.get(f'/api/v1/cards/{card_id}')
    assert get_resp.status_code == 200

    update_resp = client.put(f'/api/v1/cards/{card_id}', json={'title': 'CTO'})
    assert update_resp.status_code == 200

    delete_resp = client.delete(f'/api/v1/cards/{card_id}')
    assert delete_resp.status_code == 200
