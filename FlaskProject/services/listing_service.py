from models import Listing
from utils import Result
from extensions import db
from flask_login import current_user

def list_book(form):

    title = form.get('title')
    author = form.get('author')
    description = form.get('description')
    genre_id = int(form.get('genre_id'))
    user_id = current_user.user_id
    is_available = True

    new_listing = Listing(
        title=title,
        author=author,
        description=description,
        genre_id=genre_id,
        user_id=user_id,
        is_available=is_available
        )
    db.session.add(new_listing)
    db.session.commit()
    print(new_listing.user.username)

def get_all_listings():
    return Listing.query.all()