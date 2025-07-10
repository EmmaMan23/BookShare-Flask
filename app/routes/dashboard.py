from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services import dashboard_service

dash = Blueprint('dash', __name__)


@dash.route('/dashboard')
@login_required
def dashboard():
    """Dashboard view route, displays user and site metrics"""
    
    data = dashboard_service.read_metrics(current_user)
    return render_template('dashboard.html', metrics=data)
