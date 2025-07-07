import pytest
from app.extensions import db as _db
from app.models import User
from datetime import date


def test_register_success(client, app):
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'pass123',
        're_password': 'pass123',
        'user_type': 'admin',
        'admin_code': "Secretadmin3"
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
        'user_type': 'regular',
        'admin_code': ""
    }, follow_redirects=True)

    assert b"Unsuccessful registration, Passwords need to match!" in response.data
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
        ("notauser", "any_password"),
        ("testuser", "wrongpassword"),
        ("", "password"),
        ("testuser", ""),
        ("", ""),
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
    "new_username, old_password, new_password, confirm_password",
    [
        ("newuser", "", "", ""),
        ("olduser", "oldpass", "newpass123", "newpass123"),
        ("olduser", "oldpass", "newpass123", "wrongconfirm"),
        ("olduser", "", "newpass123", "newpass123"),
        ("takenuser", "", "", ""),
        ("olduser", "oldpass", "", ""),
    ]
)
def test_edit_user(client, app, new_username, old_password, new_password, confirm_password):
    with app.app_context():
        user = User(username='olduser', role='regular')
        user.set_password('oldpass')
        _db.session.add(user)

        taken_user = User(username='takenuser', role='regular')
        taken_user.set_password('pass')
        _db.session.add(taken_user)

        _db.session.commit()

    client.post('/login', data={'username': 'olduser',
                'password': 'oldpass'}, follow_redirects=True)

    data = {
        'form_type': 'edit',
        'username': new_username,
        'old_password': old_password,
        'new_password': new_password,
        'confirm_password': confirm_password,
    }

    response = client.post('/edit_user', data=data, follow_redirects=True)


    if new_username == "takenuser":
        assert b"Username already taken" in response.data
    elif old_password or new_password or confirm_password:
        if not all([old_password, new_password, confirm_password]):
            assert b"All fields required to change password" in response.data
        elif new_password != confirm_password:
            assert b"New password and confirmation password do not match!" in response.data
        elif old_password != "oldpass":
            assert b"Current Password entered incorrectly" in response.data
        else:
            assert b"Details updated successfully" in response.data
    elif new_username and new_username != "olduser":
        assert b"Details updated successfully" in response.data
    else:
        assert b"No changes made" in response.data

    response = client.post('/edit_user', data=data, follow_redirects=True)


import pytest

@pytest.mark.parametrize(
    "initial_marked_for_deletion, form_marked_for_deletion_value, expected_message",
    [
        (False, 'true', b"Account deletion requested. An admin will review your request"),
        (True, 'true', b"Account deletion has been cancelled"),
        (False, None, b"No changes made"),
        (True, None, b"No changes made"),
    ]
)
def test_edit_user_marked_for_deletion(client, app, initial_marked_for_deletion, form_marked_for_deletion_value, expected_message):
    with app.app_context():
        user = User(username='olduser', role='regular', marked_for_deletion=initial_marked_for_deletion)
        user.set_password('oldpass')
        _db.session.add(user)
        _db.session.commit()

    client.post('/login', data={'username': 'olduser',
                'password': 'oldpass'}, follow_redirects=True)

    data = {
        'form_type': 'delete',
    }
    if form_marked_for_deletion_value is not None:
        data['marked_for_deletion'] = form_marked_for_deletion_value

    response = client.post('/edit_user', data=data, follow_redirects=True)

    assert expected_message in response.data, \
        f"Assertion failed for initial_marked_for_deletion={initial_marked_for_deletion}, " \
        f"form_marked_for_deletion_value={form_marked_for_deletion_value}. " \
        f"Expected '{expected_message.decode()}' but got '{response.data.decode()}'"

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
