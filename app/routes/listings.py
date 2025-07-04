from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Genre, Listing, Loan
from app.services import listing_service
from datetime import date, timedelta
from app.services.listing_service import ListingService
from app.services import listing_service, dashboard_service
from app.extensions import db


listings = Blueprint ('listings', __name__)

listing_service = ListingService(db.session, dashboard_service)

@listings.route('/create_listing', methods=['POST', 'GET'])
@login_required
def create_listing():
    genres = listing_service.get_all_genres()
    if request.method == 'POST':
        form = request.form
        title = form.get('title')
        author = form.get('author')
        description = form.get('description')
        genre_id_raw = form.get('genre_id')
        genre_id = int(genre_id_raw) if genre_id_raw else None

        user_id = current_user.user_id
        is_available = True
    
        result = listing_service.list_book(title, author, description, genre_id, user_id, is_available)

        if result.success:
            flash(result.message, "success")
            return redirect(url_for('listings.view_all'))
        else:
            flash(result.message, "danger")

    return render_template('create_listing.html', genres=genres)

@listings.route('/view_listings', methods=['GET'])
@login_required
def view_all():
    args = request.args
    search_query = args.get('search')
    genre_filter = args.get('genre')
    availability_filter = args.get('availability')
    sort_order = args.get('sort', 'desc')

    marked_for_deletion = args.get('marked_for_deletion')
    if marked_for_deletion and marked_for_deletion.lower() == 'true':
        marked_for_deletion = True
    else:
        marked_for_deletion = None  

    if sort_order not in ('asc', 'desc'):
        sort_order = 'desc'

    result = listing_service.get_all_listings(
        genre=genre_filter,
        availability=(availability_filter == "available") if availability_filter else None,
        search=search_query,
        sort_order=sort_order,
        marked_for_deletion=marked_for_deletion
    )

    genres = listing_service.get_all_genres()

    return render_template(
        'view_books.html',
        listings=result.data,
        search=search_query,
        genre=genre_filter,
        availability=availability_filter,
        genres=genres,
        sort_order=sort_order,
        marked_for_deletion=marked_for_deletion,
        current_user=current_user
    )

@listings.route('/view_my_books')
@login_required
def view_mine():
    result = listing_service.get_all_listings(user_id=current_user.user_id)
    return render_template('show_user_listings.html', listings=result.data, existing_user=current_user)

@listings.route('/edit_listing', methods=['POST', 'GET'])
@login_required
def edit_listing():
    genres = listing_service.get_all_genres()

    if request.method == 'POST':
        form_data = request.form
        listing_id_str = form_data.get('listing_id')

        if not listing_id_str or not listing_id_str.isdigit():
            flash("Invalid or missing listing ID.", "danger")
            return redirect(url_for('listings.view_mine'))

        listing_id = int(listing_id_str)
        result = listing_service.get_listing_by_id(listing_id)

        if not result.success:
            flash("Listing not found.", "danger")
            return redirect(url_for('listings.view_mine'))

        listing = result.data

        # Determine availability toggle
        if 'is_available' in form_data:
            new_availability = not listing.is_available
        else:
            new_availability = listing.is_available

        res = listing_service.edit_listing(
            listing_id=listing_id,
            user_id=current_user.user_id,
            title=form_data.get('title'),
            author=form_data.get('author'),
            description=form_data.get('description'),
            genre_id=form_data.get('genre_id'),
            is_available=new_availability,
            marked_for_deletion=form_data.get('marked_for_deletion')
        )

        flash(res.message, "success" if res.success else "danger")

        if res.success:
            return redirect(url_for('listings.view_mine'))
        else:
            # On failure, re-fetch listing for rendering
            listing_result = listing_service.get_listing_by_id(listing_id)
            listing = listing_result.data if listing_result.success else None
            return render_template('edit_listing.html', genres=genres, listing=listing)

    else:
        # GET method
        listing_id = request.args.get('listing_id', type=int)
        if not listing_id:
            flash("Invalid or missing listing ID.", "danger")
            return redirect(url_for('listings.view_mine'))

        listing_result = listing_service.get_listing_by_id(listing_id)
        if not listing_result.success:
            flash("Listing not found.", "danger")
            return redirect(url_for('listings.view_mine'))

        listing = listing_result.data

        if listing.user_id != current_user.user_id:
            flash("You can't edit someone else's listing", "danger")
            return redirect(url_for('listings.view_mine'))

        return render_template('edit_listing.html', genres=genres, listing=listing)

    
@listings.route('/mark_for_deletion', methods=['POST'])
@login_required
def mark_for_deletion():
    listing_id = int(request.form.get('listing_id'))

    result = listing_service.get_listing_by_id(listing_id)
    if not result.success:
        flash("Listing not found.", "danger")
        return redirect(url_for('listings.view_mine'))

    listing = result.data  # unwrap the Listing object

    if listing.user_id != current_user.user_id:
        flash("You are not authorised to change this listing.", "danger")
        return redirect(url_for('listings.view_mine'))

    # Only take action if the checkbox was checked
    if request.form.get('marked_for_deletion') == 'true':
        # Flip the current deletion status
        is_marked = not listing.marked_for_deletion
        update_result = listing_service.update_marked_for_deletion(listing_id, is_marked)
        flash(update_result.message, "success" if update_result.success else "danger")
    else:
        flash("Please check the box to confirm your action.", "warning")

    return redirect(url_for('listings.view_mine'))


@listings.route('/view_loans')
@login_required
def view_loans():
    args = request.args
    default_scope = 'all' if current_user.is_admin else 'self'
    scope = args.get('scope', default_scope)
    status = args.get('status')
    search = args.get('search')
    sort_order = args.get('sort', 'desc')


    if scope == 'all' and current_user.is_admin:
        result = listing_service.get_all_loans(status=status, search=search, sort_order=sort_order)
    else:
        result = listing_service.get_all_loans(current_user.user_id, status=status, search=search, sort_order=sort_order)
    print(f"Scope: {scope}, Is admin: {current_user.is_admin}")
    listings_data = listing_service.get_all_listings()
    today = date.today()
    return render_template(
        'view_loans.html',
        loans=result.data,
        listings=listings_data,
        today=today,
        scope=scope,
        status=status,
        search=search,
        sort_order=sort_order
    )
        
@listings.route('/reserve_book', methods=['POST'])
@login_required
def reserve_book():
    form_data = request.form
    if 'reserve' in form_data:
        listing_id = int(form_data.get('listing_id'))
        user_id = current_user.user_id

        listing_result = listing_service.get_listing_by_id(listing_id)
        if not listing_result.success:
            flash("Listing not found.", "danger")
            return redirect(url_for('listings.view_all'))

        listing = listing_result.data

        if listing.user_id == current_user.user_id:
            flash("You cannot reserve your own book.", "warning")
            return redirect(url_for('listings.view_all'))
        
        result = listing_service.reserve_book(user_id, listing_id)
        flash(result.message, "success" if result.success else "danger")

   
        return redirect(url_for('listings.view_loans', scope='self'))



@listings.route('/update_loan', methods=['POST'])
@login_required
def update_loan():
    form_data = request.form
    if 'returned' in form_data:
        loan_id = int(form_data.get('loan_id'))
        user_id = current_user.user_id
        today = date.today()

        result, loan = listing_service.update_loan(loan_id, actual_return_date=today)
        flash(result.message, "success" if result.success else "danger")

        loan_result = listing_service.get_loan_by_id(loan_id)
        if loan_result.success:
            loan_obj = loan_result.data
            if current_user.is_admin and loan_obj.user_id != current_user.user_id:
                return redirect(url_for('listings.view_loans', scope='all'))
        
        return redirect(url_for('listings.view_loans', scope='self'))

    # fallback
    return redirect(url_for('listings.view_loans', scope='self'))






        