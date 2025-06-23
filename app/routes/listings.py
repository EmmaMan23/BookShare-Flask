from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Genre, Listing
from app.services import listing_service
from datetime import date, timedelta
from app.services.listing_service import ListingService
from app.extensions import db


listings = Blueprint ('listings', __name__)

listing_service = ListingService(db.session)

@listings.route('/create_listing', methods=['POST', 'GET'])
@login_required
def create_listing():
    genres = Genre.query.filter_by(inactive=False).all()
    if request.method == 'POST':
        form = request.form
        title = form.get('title')
        author = form.get('author')
        description = form.get('description')
        genre_id = int(form.get('genre_id'))
        user_id = current_user.user_id
        is_available = True
    
        result = listing_service.list_book(title, author, description, genre_id, user_id, is_available)

        if result.success:
            flash(result.message, "success")
            return redirect(url_for('listings.view_all'))
        else:
            flash(result.message, "danger")

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
        listing_id = int(form_data.get('listing_id'))
        listing = listing_service.get_listing_by_id(listing_id)

        if listing.user_id != current_user.user_id:
            flash("You can't edit someone else's listing")
            return redirect(url_for('listings.view_mine'))
        
        res = listing_service.edit_listing(
                listing_id=listing_id,
                user_id=current_user.user_id,
                title = form_data.get('title'),
                author = form_data.get('author'),
                description = form_data.get('description'),
                genre_id = form_data.get('genre_id'),
                is_available = form_data.get('is_available'),
                marked_for_deletion = form_data.get('marked_for_deletion'))

        flash(res.message, "success" if res.success else "danger")

        if res.success:
            return redirect(url_for('listings.view_mine'))
        else:
            listing = listing_service.get_listing_by_id(listing_id)
            return render_template('edit_listing.html', genres=genres, listing=listing)
        
    else:
        listing_id = int(request.args.get('listing_id'))
        listing = listing = listing_service.get_listing_by_id(listing_id)

        if not listing:
            flash("Listing not found.", "danger")
            return redirect(url_for('listings.view_mine'))

        if listing.user_id != current_user.user_id:
            flash("You can't edit someone else's listing", "danger")
            return redirect(url_for('listings.view_mine'))
        
        return render_template('edit_listing.html', genres=genres, listing=listing)
        
        

@listings.route('/view_loans')
@login_required
def view_loans():
    loans_data = listing_service.get_loans_current_user(current_user.user_id)
    listings_data = listing_service.get_all_listings()
    today = date.today()
    return render_template('view_loans.html', loans=loans_data, listings=listings_data, today=today, scope="self")

@listings.route('/view_all_loans')
@login_required
def view_all_loans():
    loans_data = listing_service.get_all_loans()
    listings_data = listing_service.get_all_listings()
    today = date.today()
    return render_template('view_loans.html', loans=loans_data, listings=listings_data, today=today, scope="all")

@listings.route('/reserve_book', methods=['POST'])
@login_required
def reserve_book():
    form_data = request.form
    if 'reserve' in form_data:
        listing_id = int(form_data.get('listing_id'))
        user_id = current_user.user_id

        listing = listing_service.get_listing_by_id(listing_id)
        if not listing:
            flash("Listing not found.", "danger")
            return redirect(url_for('listings.view_all'))

        if listing.user_id == current_user.user_id:
            flash("You cannot reserve your own book.", "warning")
            return redirect(url_for('listings.view_all'))
        
        result = listing_service.reserve_book(user_id, listing_id)
        flash(result.message, "success" if result.success else "danger")
        return redirect(url_for('listings.view_all'))

@listings.route('/update_loan', methods=['POST'])
@login_required
def update_loan():
    form_data = request.form
    if 'returned' in form_data:
        loan_id = int(form_data.get('loan_id'))
        user_id = current_user.user_id

        result = listing_service.update_loan(user_id, loan_id)

        flash(result.message, "success" if result.success else "danger")
    return redirect(url_for('listings.view_loans'))


        