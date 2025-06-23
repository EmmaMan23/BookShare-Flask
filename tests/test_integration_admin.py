import pytest
from app.models import User, Genre
from app.extensions import db as _db

def test_view_users_page(client, app):
    with app.app_context():
        user1 = User(username="user1", role="regular")
        user2 = User(username="user2", role="regular")
        user1.set_password("pass1")
        user2.set_password("pass2")
        _db.session.add_all([user1, user2])
        _db.session.commit()

    response = client.get('/view_users')

    assert response.status_code == 200
    assert b"user1" in response.data
    assert b"user2" in response.data


def test_create_genre_success(client, app):
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


def test_create_genre_invalid_name(client):
    response = client.post('/create_genre', data={
        'name': '   ',
        'image': 'images/fantasy.png'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Genre name cannot be empty" in response.data


def test_edit_genre_success(client, app):
    with app.app_context():
        genre = Genre(name="SciFi", image="images/science.png", inactive=False)
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
        assert updated.name == "Updated Genre"
        assert updated.image == "images/fantasy.png"


def test_delete_genre_record(client, app):
    with app.app_context():
        genre = Genre(name="To Be Deleted", image="images/horror.png", inactive=False)
        _db.session.add(genre)
        _db.session.commit()
        genre_id = genre.genre_id

    response = client.post('/delete_record', data={
        'model': 'genre',
        'id': genre_id
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Record deleted successfully" in response.data

    with app.app_context():
        assert _db.session.get(Genre, genre_id) is None
