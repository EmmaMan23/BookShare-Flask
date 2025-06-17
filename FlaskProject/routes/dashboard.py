from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from models import Genre, Listing, User
from services import admin_service


dash = Blueprint('dash', __name__)

@dash.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@dash.route('/view_users')
def view_users():
    user_data = admin_service.view_users()
    return render_template('view_users.html', users=user_data)