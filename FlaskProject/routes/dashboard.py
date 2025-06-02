from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user


dash = Blueprint('dash', __name__)

@dash.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')