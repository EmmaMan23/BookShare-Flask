from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from models import Genre
from services import listing_service

listings = Blueprint ('listings', __name__)

@listings.route('/create_listing', methods=['POST', 'GET'])
@login_required
def create_listing():

    genres = Genre.query.filter_by(inactive=False).all()

    if request.method == 'POST':
        form_data = request.form
        result = listing_service.list_book(form_data)
        
        #print(request.form.get('Title'))

    return render_template('create_listing.html', genres=genres)

@listings.route('/view_listings')
@login_required
def view_all():
    return("View all books and reserve")

@listings.route('/view_my_books')
@login_required
def view_mine():
    return("View my books and manage")

@listings.route('/view_loans')
@login_required
def view_loans():
    return("View past loans")