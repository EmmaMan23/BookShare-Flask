import pytest
from unittest.mock import MagicMock
from app.services.user_service import UserService
from app.models import User
from app.utils import Result
from werkzeug.security import generate_password_hash

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def user_service(mock_db_session):
    return UserService(db_session=mock_db_session)

def test_register_user_success(user_service, mock_db_session):
    mock_db_session.query().filter_by().first.return_value = None

    result = user_service.register_user(
        username="newuser",
        password="secret123",
        re_password="secret123",
        user_type="member",
        admin_code=""
    )

    assert result.success is True
    assert "successful" in result.message.lower()
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    
def test_register_username_taken(user_service, mock_db_session):
    mock_db_session.query().filter_by().first.return_value = MagicMock()  

    result = user_service.register_user(
        username="AUserAlready",
        password="pass",
        re_password="pass",
        user_type="regular",
        admin_code=""
    )

    assert result.success is False
    assert "username already taken" in result.message.lower()

def test_register_passwords_not_matching(user_service):
    
    result = user_service.register_user(
        username="newuser",
        password="pass",
        re_password="notpass",
        user_type="regular",
        admin_code=""
    )

    assert result.success is False
    assert "passwords need to match!" in result.message.lower()

def test_user_login_success(user_service, mock_db_session):
    fake_user = MagicMock()
    fake_user.verify_password.return_value = True

    mock_db_session.query().filter_by().first.return_value = fake_user

    result = user_service.user_login(username="correctuser", password="correctpass")

    assert result.success is True
    assert "successful login" in result.message.lower()
    assert result.data == fake_user

def test_user_login_fail(user_service, mock_db_session):
    fake_user = MagicMock()
    fake_user.verify_password.return_value = False

    mock_db_session.query().filter_by().first.return_value = fake_user

    result = user_service.user_login(username="correctuser", password="wrongpass")

    assert result.success is False
    assert "invalid username or password" in result.message.lower()

@pytest.fixture
def fake_user():
    user = MagicMock()
    user.username = "oldusername"
    user.password_hash = generate_password_hash("oldpass")
    user.marked_for_deletion = False
    user.verify_password.side_effect = lambda pw: pw == "oldpass"
    return user

def test_update_user_success_username(user_service, mock_db_session, fake_user):
    mock_db_session.query().filter_by().first.return_value = None

    result = user_service.update_user(fake_user, new_username="newuser", old_password="", new_password="", confirm_password="", marked_for_deletion=None)

    assert result.success is True
    assert "details updated successfully" in result.message.lower()
    assert fake_user.username == "newuser"
    assert mock_db_session.commit.called

def test_update_username_taken(user_service, mock_db_session, fake_user):
    mock_db_session.query().filter_by().first.return_value = MagicMock()

    result = user_service.update_user(fake_user, new_username="takenuser", old_password="", new_password="", confirm_password="", marked_for_deletion=None)

    assert result.success is False
    assert "username already taken" in result.message.lower()

def test_password_change_success(user_service, mock_db_session, fake_user):
    result = user_service.update_user(fake_user, new_username=None, old_password="oldpass", new_password="newpass", confirm_password="newpass", marked_for_deletion=None)

    assert result.success is True
    assert "details updated successfully" in result.message.lower()
    assert fake_user.password_hash != generate_password_hash("oldpass") 
    assert mock_db_session.commit.called

def test_password_change_missing_fields(user_service, fake_user):
    result = user_service.update_user(fake_user, new_username=None, old_password="oldpass", new_password="", confirm_password="", marked_for_deletion=None)

    assert result.success is False
    assert "all fields required" in result.message.lower()

def test_password_change_incorrect_old_password(user_service, fake_user):
    result = user_service.update_user(fake_user, new_username=None, old_password="wrongpass", new_password="newpass", confirm_password="newpass", marked_for_deletion=None)

    assert result.success is False
    assert "current password entered incorrectly" in result.message.lower()

def test_password_change_confirmation_mismatch(user_service, fake_user):
    result = user_service.update_user(fake_user, new_username=None, old_password="oldpass", new_password="newpass", confirm_password="diffpass", marked_for_deletion=None)

    assert result.success is False
    assert "do not match" in result.message.lower()

def test_mark_for_deletion(user_service, mock_db_session, fake_user):
    result = user_service.update_user(fake_user, new_username="", old_password="", new_password="", confirm_password="", marked_for_deletion="yes")

    assert result.success is True
    assert "deletion requested" in result.message.lower()
    assert fake_user.marked_for_deletion is True
    assert mock_db_session.commit.called

def test_unmark_for_deletion(user_service, mock_db_session, fake_user):
    fake_user.marked_for_deletion = True
    result = user_service.update_user(fake_user, new_username="", old_password="", new_password="", confirm_password="", marked_for_deletion="no")

    assert result.success is True
    assert "deletion has been cancelled" in result.message.lower()
    assert fake_user.marked_for_deletion is False
    assert mock_db_session.commit.called

def test_no_changes_made(user_service, fake_user):
    result = user_service.update_user(fake_user, new_username=None, old_password="", new_password="", confirm_password="", marked_for_deletion=None)

    assert result.success is False
    assert "no changes made" in result.message.lower()