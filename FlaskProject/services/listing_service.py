from models import Listing, Loan
from utils import Result
from extensions import db
from flask_login import current_user
from datetime import date, timedelta

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

def get_all_listings():
    return Listing.query.all()

def get_listing_by_id(listing_id):
    return Listing.query.get(listing_id)

def edit_listing(listing_id, form):
    listing = get_listing_by_id(listing_id)

    if listing.user_id != current_user.user_id:
        raise PermissionError("You can't edit someone else's listing")
    
    title = form.get('title')
    author = form.get('author')
    description = form.get('description')
    genre = form.get('genre_id')
    if genre is not None and genre != '':
        listing.genre_id = int(genre)
    else:
        genre_id = None
    is_available = form.get('is_available')
    marked_for_deletion = form.get('marked_for_deletion')

    if title:
        listing.title = title
    if author:
        listing.author = author
    if description:
        listing.description = description
    if genre_id is not None:
        listing.genre_id = int(genre_id)
    if is_available is not None:
        listing.is_available = True
    else:
        listing.is_available = False
    if marked_for_deletion is not None:
        listing.marked_for_deletion = marked_for_deletion in ['true', 'on', '1']
    else:
        listing.marked_for_deletion = False


    db.session.commit()

    

def get_all_loans():
    return Loan.query.order_by(Loan.return_date.desc()).all()

def get_loans_current_user(user_id):
    return (Loan.query
            .filter_by(user_id=user_id)
            .order_by(Loan.return_date.desc())
            .all())

def update_loan(user_id, loan_id):
    loan = Loan.query.get(loan_id)

    loan.is_returned = True
    db.session.commit()


def reserve_book(user_id, listing_id):

    start_date = date.today() + timedelta(days=1)
    return_date = start_date + timedelta(days=21)

    loan = Loan(
        user_id=user_id,
        listing_id=listing_id,
        start_date=start_date,
        return_date=return_date,
        is_returned= False
    )
    
    db.session.add(loan)

    listing = Listing.query.get(listing_id)
    if listing:
        listing.is_available = False

    db.session.commit()
    return loan