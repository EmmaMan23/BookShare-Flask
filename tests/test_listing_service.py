import pytest
from unittest.mock import MagicMock, patch
from app.services.listing_service import ListingService
from app.models import Listing, Loan
from app.utils import Result

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def listing_service(mock_db_session):
    return ListingService(mock_db_session)

def test_list_book_success(listing_service, mock_db_session):
    # Arrange: make add() and commit() just succeed
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    
    # Act
    result = listing_service.list_book(
        title="Test Book",
        author="Author",
        description="Desc",
        genre_id=1,
        user_id=123,
        is_available=True
    )
    
    # Assert
    assert result.success is True
    assert "Listing created successfully" in result.message
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_list_book_exception(listing_service, mock_db_session):
    mock_db_session.add.side_effect = Exception("DB error")
    result = listing_service.list_book(
        title="Test Book",
        author="Author",
        description="Desc",
        genre_id=1,
        user_id=123,
        is_available=True
    )
    assert result.success is False
    assert "Error creating Listing" in result.message

def test_get_all_listings_calls_query_all(listing_service, mock_db_session):
    listing_service.get_all_listings()
    mock_db_session.query.assert_called_once_with(Listing)
    mock_db_session.query.return_value.all.assert_called_once()

def test_get_listing_by_id_calls_session_get(listing_service, mock_db_session):
    listing_service.get_listing_by_id(42)
    mock_db_session.get.assert_called_once_with(Listing, 42)

def test_edit_listing_success(listing_service, mock_db_session):
    # Setup a dummy listing
    listing = Listing(title="Old", author="Old", description="Old", genre_id=1, user_id=1, is_available=True)
    listing.genre_id = 1
    # Mock get_listing_by_id to return the dummy listing
    listing_service.get_listing_by_id = MagicMock(return_value=listing)
    
    mock_db_session.commit.return_value = None
    
    result = listing_service.edit_listing(
        listing_id=1,
        user_id=1,
        title="New Title",
        author="New Author",
        description="New Desc",
        genre_id=2,
        is_available="true",
        marked_for_deletion="false"
    )
    
    assert result.success is True
    assert "Listing updated successfully" in result.message
    assert listing.title == "New Title"
    assert listing.author == "New Author"
    assert listing.description == "New Desc"
    assert listing.genre_id == 2
    assert listing.is_available is True
    assert listing.marked_for_deletion is False
    mock_db_session.commit.assert_called_once()

def test_edit_listing_not_found(listing_service):
    listing_service.get_listing_by_id = MagicMock(return_value=None)
    result = listing_service.edit_listing(
        listing_id=999,
        user_id=1
    )
    assert result.success is False
    assert result.message == "Listing not found"

def test_edit_listing_wrong_user(listing_service):
    listing = Listing(user_id=2)
    listing_service.get_listing_by_id = MagicMock(return_value=listing)
    result = listing_service.edit_listing(listing_id=1, user_id=1)
    assert result.success is False
    assert "can't edit someone else's listing" in result.message

def test_reserve_book_success(listing_service, mock_db_session):
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    
    # Mock getting a listing to mark unavailable
    listing = Listing(is_available=True)
    mock_db_session.get.return_value = listing
    
    result = listing_service.reserve_book(user_id=1, listing_id=1)
    assert result.success is True
    assert "reserved successfully" in result.message
    assert listing.is_available is False
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()

def test_reserve_book_exception(listing_service, mock_db_session):
    mock_db_session.add.side_effect = Exception("DB failure")
    result = listing_service.reserve_book(user_id=1, listing_id=1)
    assert result.success is False
    assert "Error reserving book" in result.message

def test_update_loan_success(listing_service, mock_db_session):
    loan = Loan(is_returned=False)
    mock_db_session.get.return_value = loan
    mock_db_session.commit.return_value = None

    result = listing_service.update_loan(user_id=1, loan_id=1)
    assert result.success is True
    assert "marked as returned" in result.message
    assert loan.is_returned is True
    mock_db_session.commit.assert_called_once()

def test_update_loan_not_found(listing_service, mock_db_session):
    mock_db_session.get.return_value = None
    result = listing_service.update_loan(user_id=1, loan_id=999)
    assert result.success is False
    assert "Loan not found" in result.message
