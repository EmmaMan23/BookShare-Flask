import pytest
from unittest.mock import MagicMock, patch
from app.services.listing_service import ListingService
from app.models import Listing, Loan, User
from app.utils import Result
from datetime import date

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def listing_service(mock_db_session):
    return ListingService(mock_db_session)

def test_list_book_success(mock_db_session):
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)
  
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    

    result = listing_service.list_book(
        title="Test Book",
        author="Author",
        description="Desc",
        genre_id=1,
        user_id=123,
        is_available=True
    )
    

    assert result.success is True
    assert "Listing created successfully" in result.message
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_list_book_exception(mock_db_session):
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)
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

def test_get_all_listings_calls_query_all(mock_db_session):
    mock_query = MagicMock()
    
    mock_query.options.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = []

    mock_db_session.query.return_value = mock_query

    mock_dashboard_service = MagicMock()
    ListingService(mock_db_session, mock_dashboard_service)


def test_get_listing_by_id_calls_session_get(mock_db_session):
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)
    listing_service.get_listing_by_id(42)
    mock_db_session.get.assert_called_once_with(Listing, 42)

from unittest.mock import patch

@patch('app.services.listing_service.current_user')
def test_edit_listing_success(mock_current_user, mock_db_session):
    mock_current_user.is_admin = False  

    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)

    listing = Listing(title="Old", author="Old", description="Old", genre_id=1, user_id=1, is_available=True)
    listing.genre_id = 1
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
        marked_for_deletion="false",
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


def test_edit_listing_not_found():
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)
    listing_service.get_listing_by_id = MagicMock(return_value=None)
    result = listing_service.edit_listing(
        listing_id=999,
        user_id=1
    )
    assert result.success is False
    assert result.message == "Listing not found"

@patch("app.services.listing_service.current_user")
def test_edit_listing_wrong_user(mock_current_user):
    
    mock_dashboard_service = MagicMock()
    mock_current_user.is_admin = False

    listing_service = ListingService(mock_db_session, mock_dashboard_service)
    listing = Listing(user_id=2)
    listing_service.get_listing_by_id = MagicMock(return_value=listing)
    result = listing_service.edit_listing(listing_id=1, user_id=1)
    assert result.success is False
    assert "can't edit someone else's listing" in result.message

def test_reserve_book_success(mock_db_session):
    user_id = 1
    listing_id = 101
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)
    mock_user = User(user_id=user_id, username="testuser", total_loans=0)
    mock_listing = Listing(listing_id=listing_id, title="Test Book", is_available=True)

    mock_db_session.get.side_effect = lambda model, id: {
        User: mock_user,
        Listing: mock_listing
    }.get(model)

    result = listing_service.reserve_book(user_id, listing_id)

    assert result.success is True
    assert "Book reserved successfully" in result.message
    assert isinstance(result.data, Loan)
    assert result.data.user_id == user_id
    assert result.data.listing_id == listing_id
    assert result.data.is_returned is False
    assert mock_listing.is_available is False
    assert mock_user.total_loans == 1

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_dashboard_service.update_overall_loans.assert_called_once()



def test_reserve_book_exception(mock_db_session):
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)
    mock_db_session.add.side_effect = Exception("DB failure")
    result = listing_service.reserve_book(user_id=1, listing_id=1)
    assert result.success is False
    assert "Error reserving book" in result.message

def test_update_loan_success(mock_db_session):
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)
    loan = Loan(is_returned=False)
    mock_db_session.get.return_value = loan
    mock_db_session.commit.return_value = None

    result, _ = listing_service.update_loan(loan_id=1, actual_return_date=date.today())
    assert result.success is True

    assert result.success is True
    assert "loan marked as returned" in result.message.lower()
    assert loan.is_returned is True
    mock_db_session.commit.assert_called_once()


def test_update_loan_not_found(mock_db_session):
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)

    mock_db_session.get.return_value = None
    result, loan = listing_service.update_loan(loan_id=999, actual_return_date=None)
    assert result.success is False
    assert "Loan not found" in result.message

