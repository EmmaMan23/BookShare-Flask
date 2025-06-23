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


@pytest.mark.parametrize(
    "username,password",
    [
        ("notauser", "any_password"),  # username not in DB
        ("testuser", "wrongpassword"),  # valid user, wrong pass
        ("", "password"),  # empty username
        ("testuser", ""),  # empty password
        ("", ""),  # both empty
    ]
)

def test_login_invalid_details(client, app, username, password):
    with app.app_context():
        if username == "testuser":
            user = User(username='testuser', role='regular')
            user.set_password('correctpassword')
            _db.session.add(user)
            _db.session.commit()

    response = client.post('/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)

    if username == "" or password == "":
        assert b"Username" in response.data or b"Password" in response.data
    else:
        assert b"Invalid username or password" in response.data

@pytest.mark.parametrize(
    "new_username, old_password, new_password, confirm_password, marked_for_deletion",
    [
        ("newuser", "", "", "", ""),
        ("", "oldpass", "newpass123", "newpass123", ""),
        ("", "oldpass", "newpass123", "wrongconfirm", ""),
        ("", "", "newpass123", "newpass123", ""),
        ("takenuser", "", "", "", ""),
        ("", "", "", "", ""),
        ("", "", "", "", "yes"),
        ("", "", "", "", "no"),
    ]
)
def test_edit_user(client, app, new_username, old_password, new_password, confirm_password, marked_for_deletion):
    with app.app_context():
        # Setup users
        user = User(username='olduser', role='regular')
        user.set_password('oldpass')
        _db.session.add(user)

        taken_user = User(username='takenuser', role='regular')
        taken_user.set_password('pass')
        _db.session.add(taken_user)

        _db.session.commit()

    # Login the user
    client.post('/login', data={'username': 'olduser', 'password': 'oldpass'}, follow_redirects=True)

    data = {
        'username': new_username,
        'old_password': old_password,
        'new_password': new_password,
        'confirm_password': confirm_password,
        'marked_for_deletion': marked_for_deletion
    }

    # Post without follow_redirects
    response = client.post('/edit_user', data=data, follow_redirects=False)
    print(response.request.path)
    assert response.status_code == 302

    # Follow the redirect manually
    redirect_url = response.headers['Location']
    response2 = client.get(redirect_url)
    page_content = response2.data.decode()

    # Conditional asserts on flash messages
    if new_username == "takenuser":
        assert "Username already taken" in page_content
    elif old_password or new_password or confirm_password:
        if not all([old_password, new_password, confirm_password]):
            assert "All fields required to change password" in page_content
        elif new_password != confirm_password:
            assert "New password and confirmation password do not match!" in page_content
        elif old_password and old_password != "oldpass":
            assert "Current Password entered incorrectly" in page_content
        else:
            assert "Details updated successfully" in page_content
    elif marked_for_deletion == "yes":
        assert "Account deletion requested. An admin will review your request" in page_content
    elif new_username and new_username != "olduser":
        assert "Details updated successfully" in page_content
    else:
        assert "No changes made" in page_content

    print(response.request.path)

def test_logout(client, app):
    with app.app_context():
        user = User(username='logoutuser', role='regular')
        user.set_password('logoutpass')
        _db.session.add(user)
        _db.session.commit()

    client.post('/login', data={
        'username': 'logoutuser',
        'password': 'logoutpass',
    }, follow_redirects=True)

    response = client.post('/logout', follow_redirects=True)

    assert b"Login" in response.data

    assert b"You have been logged out" in response.data
