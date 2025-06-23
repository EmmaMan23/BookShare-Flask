import pytest
from unittest.mock import MagicMock
from app import create_app
from app.extensions import db as _db
from app.services.user_service import UserService
from app.models import User
from app.utils import Result



def test_register_success(client, app):
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'pass123',
        're_password': 'pass123',
        'user_type': 'admin'
    }, follow_redirects=True)

    assert b"Registration successful" in response.data

    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user is not None

def test_register_password_mismatch(client):
    response = client.post('/register', data={
        'username': 'testuser2',
        'password': 'pass123',
        're_password': 'differentpass',
        'user_type': 'regular'
    }, follow_redirects=True)

    assert b"Passwords do not match" in response.data
    assert b"Register" in response.data  

def test_login_success(client, app):
    with app.app_context():
        user = User(username='testloginuser', role='regular')
        user.set_password('mypassword')
        _db.session.add(user)
        _db.session.commit()

    response = client.post('/login', data={
        'username': 'testloginuser',
        'password': 'mypassword',
    }, follow_redirects=True)

    assert b"Successful login" in response.data

    response = client.get('/dashboard')
    assert b"Welcome" in response.data



