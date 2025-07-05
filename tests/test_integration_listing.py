import pytest
from app.models import User, Genre, Listing
from app.extensions import db as _db
from datetime import date


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            username="testuser",
            role="regular",
            total_loans=0,
            total_listings=0
        )
        user.set_password("testpass")
        _db.session.add(user)
        _db.session.commit()
        yield user


@pytest.fixture
def other_user(app):
    with app.app_context():
        user = User(
            username="otheruser",
            role="regular",
            total_loans=0
        )
        user.set_password("otherpass")
        _db.session.add(user)
        _db.session.commit()
        yield user


@pytest.fixture
def test_genre(app):
    with app.app_context():
        genre = Genre(
            name="Test Genre",
            image="images/romance.png"
        )
        _db.session.add(genre)
        _db.session.commit()
        yield genre


@pytest.fixture
def logged_in_client(client, test_user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.user_id)
    yield client


def test_create_listing_route_success(logged_in_client, test_genre):
    response = logged_in_client.post('/create_listing', data={
        'title': 'Integration Test Book',
        'author': 'Test Author',
        'description': 'Test Description',
        'genre_id': str(test_genre.genre_id),
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Listing created successfully" in response.data

    with logged_in_client.application.app_context():
        listing = Listing.query.filter_by(
            title='Integration Test Book').first()
        assert listing is not None


def test_edit_listing_route_success(logged_in_client, test_user, test_genre):
    with logged_in_client.application.app_context():
        listing = Listing(
            title="Old Title",
            author="Old Author",
            description="Old Desc",
            genre_id=test_genre.genre_id,
            user_id=test_user.user_id,
            is_available=True
        )
        _db.session.add(listing)
        _db.session.commit()
        listing_id = listing.listing_id

    response = logged_in_client.post('/edit_listing', data={
        'listing_id': str(listing_id),
        'title': 'New Title',
        'author': 'New Author',
        'description': 'New Description',
        'genre_id': str(test_genre.genre_id),
        'is_available': 'true',
        'marked_for_deletion': 'false'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Listing updated successfully" in response.data

    with logged_in_client.application.app_context():
        updated = _db.session.get(Listing, listing_id)
        assert updated.title == 'New Title'
        assert updated.author == 'New Author'


def test_reserve_book_route_success(logged_in_client, other_user, test_genre):
    with logged_in_client.application.app_context():
        listing = Listing(
            title="Book to Reserve",
            author="Author",
            description="Desc",
            genre_id=test_genre.genre_id,
            user_id=other_user.user_id,
            is_available=True,
            date_listed=date.today(),
        )
        _db.session.add(listing)
        _db.session.commit()
        listing_id = listing.listing_id

    response = logged_in_client.post('/reserve_book', data={
        'reserve': 'Reserve',
        'listing_id': str(listing_id)
    }, follow_redirects=True)

    assert response.status_code == 200

    if b"book reserved successfully" not in response.data.lower():
        print("Response HTML on failure:")
        print(response.data.decode())

    assert b"book reserved successfully" in response.data.lower()

    with logged_in_client.application.app_context():
        reserved_listing = _db.session.get(Listing, listing_id)
        assert reserved_listing.is_available is False


def test_view_listings_route(logged_in_client):
    response = logged_in_client.get('/view_listings')
    assert response.status_code == 200
    assert b"Listings" in response.data or b"Books" in response.data
