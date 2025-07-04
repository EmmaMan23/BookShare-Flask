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
    with patch('app.services.listing_service.validate_non_empty_string', side_effect=lambda val, field: val), \
        patch('app.models.Listing.save', return_value=True) as mock_save:

        mock_user =MagicMock()
        mock_user.total_listings = 0
        mock_db_session.get.return_value = mock_user

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
        mock_save.assert_called_once()
        mock_dashboard_service.update_overall_listings.assert_called_once()
        mock_db_session.get.assert_called_with(User, 123)
        

def test_list_book_exception(mock_db_session):

    mock_user = MagicMock()
    mock_user.total_listings = 0
    mock_db_session.get.return_value = mock_user

    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)

    with patch('app.models.Listing.save', side_effect=Exception("DB error")):
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

    mock_user = MagicMock()
    mock_user.total_loans = 0

    mock_listing = MagicMock()
    mock_listing.is_available = True

    mock_db_session.get.side_effect = lambda model, id: {
        User: mock_user,
    }.get(model)
    
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)

    with patch.object(Listing, 'get_by_id', return_value=mock_listing), \
        patch.object(mock_listing, 'save', return_value=True) as mock_listing_save, \
        patch.object(mock_user, 'save', return_value=True) as mock_user_save, \
        patch('app.models.Loan.save', return_value=True) as mock_loan_save:

        result = listing_service.reserve_book(user_id, listing_id)

        assert result.success is True
        assert "Book reserved successfully" in result.message

        assert result.data.user_id == user_id
        assert result.data.listing_id == listing_id
        assert result.data.is_returned is False

        assert mock_listing.is_available is False

        assert mock_user.total_loans == 1

        mock_listing_save.assert_called_once()
        mock_loan_save.assert_called_once()
        mock_user_save.assert_called_once()
        
        mock_dashboard_service.update_overall_loans.assert_called_once()

def test_reserve_book_exception(mock_db_session):
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)

    mock_user = MagicMock()
    mock_listing = MagicMock()
    mock_listing.save.side_effect = Exception("DB failure")
    mock_db_session.get.side_effect = lambda model, id: {
        User: mock_user,
    }.get(model)

    with patch.object(Listing, 'get_by_id', return_value=mock_listing):
        result = listing_service.reserve_book(user_id=1, listing_id=1)
        assert result.success is False
        assert "Error reserving book" in result.message

def test_update_loan_success(mock_db_session):

    mock_loan = MagicMock()
    mock_listing = MagicMock()
    mock_loan.is_returned=False
    mock_listing.is_available=False
    mock_loan.listing_id = 1 

    mock_loan.listing = mock_listing

    mock_dashboard_service = MagicMock()

    mock_db_session.get.side_effect = lambda model, id: {
    Listing: mock_listing,
    }.get(model)


    listing_service = ListingService(mock_db_session, mock_dashboard_service)
    with patch.object(mock_listing, 'save', return_value=True) as mock_listing_save, \
        patch.object(mock_loan, 'save', return_value=True) as mock_loan_save, \
        patch.object(Loan, 'get_by_id', return_value=mock_loan):

        result, _ = listing_service.update_loan(loan_id=1, actual_return_date=date.today())
        assert result.success is True

        assert result.success is True
        assert "loan marked as returned" in result.message.lower()
        assert mock_loan.is_returned is True
        assert mock_listing.is_available is True
        mock_listing_save.assert_called_once()
        mock_loan_save.assert_called_once()
        

def test_update_loan_not_found(mock_db_session):
    mock_dashboard_service = MagicMock()
    listing_service = ListingService(mock_db_session, mock_dashboard_service)

    with patch('app.models.Loan.get_by_id', return_value=None):
    
        result, loan = listing_service.update_loan(loan_id=999, actual_return_date=None)
        assert result.success is False
        assert "Loan not found" in result.message

