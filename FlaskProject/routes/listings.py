from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user

listings = Blueprint ('listings', __name__)

@listings.route('/create_listing', methods=['POST', 'GET'])
@login_required
def create_listing():
    return("List books here")

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