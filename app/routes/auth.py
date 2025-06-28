from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash, session, request, render_template
from app.services import user_service
from flask_login import login_user, logout_user, current_user, login_required
from app.services.user_service import UserService
from app.services.dashboard_service import DashboardService
from app.extensions import db


auth = Blueprint('auth', __name__)
dashboard_service = DashboardService(db.session, "app/static/metrics.json")
user_service = UserService(db.session)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    metrics = dashboard_service.read_metrics(user=None)
    if request.method == 'POST':
        form_data = request.form
        username = form_data.get('username', '').lower()
        password = form_data.get('password', '')
        re_password = form_data.get('re_password', '')
        user_type = form_data.get('user_type', '')
        admin_code = form_data.get('admin_code', '')

        result = user_service.register_user(username, password, re_password, user_type, admin_code)

        if result.success:
            flash(result.message, "success")
            return redirect(url_for('auth.login'))
        else:
            flash(result.message, "danger")
            return render_template('login.html', show_register=True, metrics=metrics) #keep showing register form if registration failed
        
    return render_template('login.html', show_register=False, metrics=metrics)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    metrics = dashboard_service.read_metrics(user=None)
    if request.method == 'POST':
        form_data = request.form

        username = form_data.get('username', '').lower()
        password = form_data.get('password', '')

        result = user_service.user_login(username, password)

        if result.success:
            login_user(result.data)
            flash(result.message, "success")
            return redirect(url_for('dash.dashboard'))
        else:
            flash(result.message, "danger")
            return render_template('login.html', show_register=False)
    return render_template('login.html', show_register=False, metrics=metrics)

@auth.route('/edit_user', methods=['POST', 'GET'])
@login_required
def edit_user():
    
    
    if request.method == 'POST':
        form_data = request.form
        new_username = form_data.get('username', '').strip()
        old_password = form_data.get('old_password', '').strip()
        new_password = form_data.get('new_password', '').strip()
        confirm_password = form_data.get('confirm_password', '').strip()
        marked_for_deletion = form_data.get('marked_for_deletion', None)

        result = user_service.update_user(
            current_user,
            new_username,
            old_password,
            new_password,
            confirm_password,
            marked_for_deletion
            )
        
        
        flash(result.message, 'success' if result.success else 'danger')
        return redirect(url_for('dash.dashboard' if result.success else 'auth.edit_user'))
    
    return render_template('edit_user.html')


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    result = user_service.user_logout()
    flash(result.message, "success" if result.success else "danger")
    return redirect(url_for('auth.login'))
