from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from models import Genre
from services import listing_service
from datetime import date, timedelta

listings = Blueprint ('listings', __name__)

@listings.route('/create_listing', methods=['POST', 'GET'])
@login_required
def create_listing():

    genres = Genre.query.filter_by(inactive=False).all()

    if request.method == 'POST':
        form_data = request.form
        result = listing_service.list_book(form_data)

    return render_template('create_listing.html', genres=genres)

@listings.route('/view_listings')
@login_required
def view_all():
    listings_data = listing_service.get_all_listings()
    return render_template('view_books.html', listings=listings_data)

@listings.route('/view_my_books')
@login_required
def view_mine():
    listings_data = listing_service.get_all_listings()
    return render_template('show_user_listings.html', listings=listings_data, existing_user=current_user) 

@listings.route('/view_loans')
@login_required
def view_loans():
    loans_data = listing_service.get_loans_current_user(current_user.user_id)
    listings_data = listing_service.get_all_listings()
    today = date.today()
    return render_template('view_loans.html', loans=loans_data, listings=listings_data, today=today)

@listings.route('/reserve_book', methods=['POST'])
def reserve_book():

    
    form_data = request.form
    if 'reserve' in form_data:
        listing_id = form_data.get('listing_id')
        user_id = current_user.user_id
        listing_service.reserve_book(user_id, int(listing_id))
        return redirect(url_for('listings.view_all'))



    