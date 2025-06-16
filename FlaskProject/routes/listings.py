from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from models import Genre, Listing
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

@listings.route('/edit_listing', methods=['POST', 'GET'])
@login_required
def edit_listing():
    genres = Genre.query.filter_by(inactive=False).all()
    if request.method == 'POST':
        form_data = request.form
        listing_id = form_data.get('listing_id')
        listing = listing_service.get_listing_by_id(listing_id)
        if listing.user_id != current_user.user_id:
            flash("You can't edit someone else's listing")
            return redirect(url_for('listings.view_mine'))
        
        try:
            listing_service.edit_listing(listing_id, form_data)
            flash("Listing updated successfully!")
        except Exception as e:
            flash(f"An error occurred: {e}")
        
        return redirect(url_for('listings.view_mine'))
    
    else:
        listing_id = request.args.get('listing_id')
        listing = listing = listing_service.get_listing_by_id(listing_id)

        if listing.user_id != current_user.user_id:
            flash("You can't edit someone else's listing")
            return redirect(url_for('listings.view_mine'))
        
        return render_template('edit_listing.html', genres=genres, listing=listing)


        



@listings.route('/view_loans')
@login_required
def view_loans():
    loans_data = listing_service.get_loans_current_user(current_user.user_id)
    listings_data = listing_service.get_all_listings()
    today = date.today()
    return render_template('view_loans.html', loans=loans_data, listings=listings_data, today=today, scope="self")

@listings.route('/reserve_book', methods=['POST'])
def reserve_book():

    
    form_data = request.form
    if 'reserve' in form_data:
        listing_id = form_data.get('listing_id')
        user_id = current_user.user_id
        listing_service.reserve_book(user_id, int(listing_id))
        return redirect(url_for('listings.view_all'))



@listings.route('/update_loan', methods=['POST'])
def update_loan():

    form_data = request.form
    if 'returned' in form_data:
        loan_id = form_data.get('loan_id')
        user_id = current_user.user_id
        listing_service.update_loan(user_id, int(loan_id))
    return redirect(url_for('listings.view_loans'))

@listings.route('/create_genre', methods=['POST', 'GET'])
def create_genre():
    form_data = request.form
    if request.method == 'GET':
        print("hey")

        return render_template('add_genre.html')
        