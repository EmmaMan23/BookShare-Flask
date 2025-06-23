import pytest
from unittest.mock import MagicMock, patch
from app.services.admin_service import AdminService
from app.models import User, Genre, Listing, Loan
from app.utils import Result

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def admin_service(mock_db_session):
    return AdminService(db_session=mock_db_session)

def test_view_users_success(admin_service, mock_db_session):
    mock_user1 = MagicMock()
    mock_user1.id = 1
    mock_user1.username = "testuser1"

    mock_user2 = MagicMock()
    mock_user2.id = 2
    mock_user2.username = "testuser2"

    mock_db_session.query.return_value.all.return_value = [mock_user1, mock_user2]

    result = admin_service.view_users()

    assert result.success is True
    assert "Users retrieved successfully" in result.message
    assert result.data == [mock_user1, mock_user2]
    mock_db_session.query.assert_called_with(User)

def test_delete_record_success(admin_service, mock_db_session):
    mock_record = MagicMock()
    mock_db_session.get.return_value = mock_record

    result = admin_service.delete_record(User, 1)

    assert result.success is True
    assert "Record deleted successfully" in result.message
    mock_db_session.get.assert_called_with(User, 1)
    mock_db_session.delete.assert_called_with(mock_record)
    mock_db_session.commit.assert_called_once()

def test_delete_record_not_found(admin_service, mock_db_session):
    mock_db_session.get.return_value = None

    result = admin_service.delete_record(Genre, 99)

    assert result.success is False
    assert "Record not found." in result.message
    mock_db_session.get.assert_called_with(Genre, 99)
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()

@patch('app.services.admin_service.validate_non_empty_string', side_effect=lambda name, field: name)
def test_create_genre_success(mock_validate_string, admin_service, mock_db_session):
    genre_name = "New Fantasy"
    genre_image = "images/fantasy.png"
    genre_inactive = False

    result = admin_service.create_genre(genre_name, genre_image, genre_inactive)

    assert result.success is True
    assert "Genre created successfully" in result.message
    mock_validate_string.assert_called_with(genre_name, "Genre name")
    mock_db_session.add.assert_called_once()
    added_genre = mock_db_session.add.call_args[0][0]
    assert added_genre.name == genre_name
    assert added_genre.image == genre_image
    assert added_genre.inactive == genre_inactive
    mock_db_session.commit.assert_called_once()

@patch('app.services.admin_service.validate_non_empty_string', side_effect=ValueError("Genre name cannot be empty."))
def test_create_genre_invalid_name(mock_validate_string, admin_service, mock_db_session):
    result = admin_service.create_genre("", "images/test.png", False)

    assert result.success is False
    assert "Genre name cannot be empty." in result.message
    mock_validate_string.assert_called_with("", "Genre name")
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

def test_get_genres_success(admin_service, mock_db_session):
    mock_genre1 = MagicMock()
    mock_genre1.id = 1
    mock_genre1.name = "Action"
    mock_genre2 = MagicMock()
    mock_genre2.id = 2
    mock_genre2.name = "Comedy"

    mock_db_session.query.return_value.all.return_value = [mock_genre1, mock_genre2]

    result = admin_service.get_genres()

    assert result.success is True
    assert "Genres returned successfully" in result.message
    assert result.data == [mock_genre1, mock_genre2]
    mock_db_session.query.assert_called_with(Genre)

@patch('app.services.admin_service.validate_non_empty_string', side_effect=lambda name, field: name)
def test_edit_genre_success(mock_validate_string, admin_service, mock_db_session):
    mock_genre = MagicMock()
    mock_genre.id = 1
    mock_genre.name = "Old Name"
    mock_genre.image = "old_image.png"

    mock_db_session.get.return_value = mock_genre

    new_name = "Updated Name"
    new_image = "new_image.png"

    result = admin_service.edit_genre(mock_genre.id, new_name, new_image)

    assert result.success is True
    assert "Genre updated successfully" in result.message
    mock_validate_string.assert_called_with(new_name, "Genre name")
    assert mock_genre.name == new_name
    assert mock_genre.image == new_image
    mock_db_session.get.assert_called_with(Genre, mock_genre.id)
    mock_db_session.commit.assert_called_once()

def test_edit_genre_no_id(admin_service, mock_db_session):
    result = admin_service.edit_genre(None, "Some Name", "Some Image")

    assert result.success is False
    assert "No genre ID provided." in result.message
    mock_db_session.get.assert_not_called()
    mock_db_session.commit.assert_not_called()

def test_edit_genre_not_found(admin_service, mock_db_session):
    mock_db_session.get.return_value = None

    result = admin_service.edit_genre(999, "New Name", "New Image")

    assert result.success is False
    assert "Genre not found." in result.message
    mock_db_session.get.assert_called_with(Genre, 999)
    mock_db_session.commit.assert_not_called()

@patch('app.services.admin_service.validate_non_empty_string', side_effect=ValueError("Genre name cannot be empty."))
def test_edit_genre_invalid_name(mock_validate_string, admin_service, mock_db_session):
    mock_genre = MagicMock()
    mock_genre.id = 1
    mock_genre.name = "Valid Name"
    mock_genre.image = "valid_image.png"
    mock_db_session.get.return_value = mock_genre

    result = admin_service.edit_genre(mock_genre.id, "", "new_image.png")

    assert result.success is False
    assert "Genre name cannot be empty." in result.message
    mock_validate_string.assert_called_with("", "Genre name")
    mock_db_session.commit.assert_not_called()
