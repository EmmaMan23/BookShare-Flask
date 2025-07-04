import pytest
from unittest.mock import MagicMock, patch
from app.services.admin_service import AdminService
from app.models import User, Genre, Listing, Loan
from app.utils import Result
from types import SimpleNamespace

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def admin_service(mock_db_session):
    return AdminService(db_session=mock_db_session)

def test_view_users_success(admin_service, mock_db_session):
    mock_user1 = MagicMock(id=1, username="testuser1")
    mock_user2 = MagicMock(id=2, username="testuser2")

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = [mock_user1, mock_user2]

    mock_db_session.query.return_value = mock_query

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
    mock_record.delete.assert_called_once_with(mock_db_session)

def test_delete_record_not_found(admin_service, mock_db_session):
    mock_db_session.get.return_value = None

    result = admin_service.delete_record(Genre, 99)

    assert result.success is False
    assert "Record not found." in result.message
    mock_db_session.get.assert_called_with(Genre, 99)
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()

def test_edit_genre_success(admin_service, mock_db_session):
    with patch('app.services.admin_service.validate_non_empty_string', side_effect=lambda name, field: name) as mock_validate_string:
        mock_genre = SimpleNamespace(id=1, name="Old Name", image="old_image.png")
        mock_genre.save = MagicMock(return_value=True)
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
        mock_genre.save.assert_called_once_with(mock_db_session)

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

def test_edit_genre_invalid_name(admin_service, mock_db_session):
    with patch('app.services.admin_service.validate_non_empty_string', side_effect=ValueError("Genre name cannot be empty.")) as mock_validate_string:
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

def test_create_genre_invalid_name(admin_service, mock_db_session):
    with patch('app.services.admin_service.validate_non_empty_string', side_effect=ValueError("Genre name cannot be empty.")) as mock_validate_string:
        result = admin_service.create_genre("", "images/test.png")

        assert result.success is False
        assert "Genre name cannot be empty." in result.message
        mock_validate_string.assert_called_with("", "Genre name")
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
