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
    else:
        listing.title = form.get('title')
        listing.author = form.get('author')
        listing.description = form.get('description')
        listing.genre_id = int(form.get('genre_id'))
       # listing.is_available = form.get('is_available')

        db.session.commit()

    

def get_all_loans():
    return Loan.query.all()

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