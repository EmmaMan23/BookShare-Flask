from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.admin_service import AdminService
from flask import jsonify
from app.extensions import db


dash = Blueprint('dash', __name__)

admin_service = AdminService(db.session)

@dash.route('/dashboard')
@login_required
def dashboard():
    data = admin_service.metrics()
    return render_template('dashboard.html', metrics=data)

