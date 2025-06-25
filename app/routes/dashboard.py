from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app.services import dashboard_service, listing_service
from flask import jsonify
from app.extensions import db

dash = Blueprint('dash', __name__)

@dash.route('/dashboard')
@login_required
def dashboard():
    data = dashboard_service.read_metrics(current_user)
    return render_template('dashboard.html', metrics=data)






























































