import pytest
from app.models import User, Genre
from app.extensions import db as _db
from datetime import date


@pytest.fixture
def genre_to_delete(app):
    with app.app_context():
        genre = Genre(name="To Be Deleted", image="images/horror.png")
        _db.session.add(genre)
        _db.session.commit()
        yield genre


@pytest.fixture
def regular_user(app):
    with app.app_context():
        user = User(username="regular", role="regular",
                    join_date=date.today(), total_loans=0, total_listings=0)
        user.set_password("password")
        _db.session.add(user)
        _db.session.commit()
        yield user


@pytest.fixture
def admin_user(app):
    with app.app_context():
        admin = User(username="admin", role="admin",
                    join_date=date.today(), total_loans=0, total_listings=0)
        admin.set_password("password")
        _db.session.add(admin)
        _db.session.commit()
        yield admin


def login_client(client, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.user_id)


def test_view_users_page(client, app, admin_user):
    with app.app_context():
        user1 = User(username="user1", role="regular",
                     join_date=date.today(), total_loans=0, total_listings=0)
        user2 = User(username="user2", role="regular",
                     join_date=date.today(), total_loans=0, total_listings=0)

        user1.set_password("pass1")
        user2.set_password("pass2")
        _db.session.add_all([user1, user2])
        _db.session.commit()

    with app.app_context():
        users = User.query.all()


    login_client(client, admin_user)

    response = client.get('/view_users', follow_redirects=True)


    assert response.status_code == 200
    assert b"user1" in response.data.lower()
    assert b"user2" in response.data.lower()


def test_create_genre_success(client, app, admin_user):
    login_client(client, admin_user)

    with app.app_context():
        genre_count = Genre.query.count()

    response = client.post('/create_genre', data={
        'name': 'New Genre',
        'image': 'images/fantasy.png'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Genre created successfully" in response.data

    with app.app_context():
        assert Genre.query.count() == genre_count + 1


def test_create_genre_invalid_name(client, admin_user):
    login_client(client, admin_user)

    response = client.post('/create_genre', data={
        'name': '   ',
        'image': 'images/fantasy.png'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Genre name cannot be empty" in response.data


def test_edit_genre_success(client, app, admin_user):
    login_client(client, admin_user)

    with app.app_context():
        genre = Genre(name="SciFi", image="images/science.png")
        _db.session.add(genre)
        _db.session.commit()
        genre_id = genre.genre_id

    response = client.post('/edit_genre', data={
        'id': genre_id,
        'name': 'Updated Genre',
        'image': 'images/fantasy.png'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Genre updated successfully" in response.data

    with app.app_context():
        updated = _db.session.get(Genre, genre_id)
        assert updated.name == "Updated genre"
        assert updated.image == "images/fantasy.png"


def test_delete_genre_record_non_admin(client, regular_user, genre_to_delete):
    login_client(client, regular_user)

    response = client.post('/delete_record', data={
        'model': 'genre',
        'id': genre_to_delete.genre_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Admin access required." in response.data

    with client.application.app_context():
        assert _db.session.get(Genre, genre_to_delete.genre_id) is not None


def test_delete_genre_record_admin(client, admin_user, genre_to_delete):
    login_client(client, admin_user)

    response = client.post('/delete_record', data={
        'model': 'genre',
        'id': genre_to_delete.genre_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Record deleted successfully" in response.data

    with client.application.app_context():
        assert _db.session.get(Genre, genre_to_delete.genre_id) is None
