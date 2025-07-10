from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services import user_service
from flask_login import login_user, logout_user, current_user, login_required
from app.services.user_service import UserService
from app.services.dashboard_service import DashboardService
from app.extensions import db
from app.utils import flash_result


auth = Blueprint('auth', __name__)
dashboard_service = DashboardService(db.session, "app/static/metrics.json")
user_service = UserService(db.session)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """ Route to POST details from the register form """

    metrics = dashboard_service.read_metrics(user=None)
    if request.method == 'POST':
        form_data = request.form
        username = form_data.get('username', '').lower()
        password = form_data.get('password', '')
        re_password = form_data.get('re_password', '')
        user_type = form_data.get('user_type', '')
        admin_code = form_data.get('admin_code', '')

        result = user_service.register_user(
            username, password, re_password, user_type, admin_code)

        flash_result(result)

#Redirect to login page if successful, continue to show register form if unsuccessful
        if result.success:
            return redirect(url_for('auth.login'))
        else:
            return render_template('login.html', show_register=True, metrics=metrics)

    return render_template('login.html', show_register=False, metrics=metrics)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Route to POST details from the login form """

    metrics = dashboard_service.read_metrics(user=None)
    if request.method == 'POST':
        form_data = request.form

        username = form_data.get('username', '').lower()
        password = form_data.get('password', '')

        result = user_service.user_login(username, password)
        
#Redirect to the dashboard if successful and the login page if unsuccessful
        if result.success:
            login_user(result.data)
            flash_result(result)
            return redirect(url_for('dash.dashboard'))
        else:
            flash_result(result)
            return render_template('login.html', show_register=False)
    return render_template('login.html', show_register=False, metrics=metrics)

@auth.route('/edit_user', methods=['POST', 'GET'])
@login_required
def edit_user():
    """ POST and GET route for the edit user form, allows users to edit 
    their account details and request a deletion of their account """

    if request.method == 'POST':
        form_data = request.form
        form_type = form_data.get('form_type')

    #Checks if the user wants to request deletion
        if form_type == 'delete':
            marked_for_deletion = form_data.get('marked_for_deletion')
            result = user_service.update_user(
                current_user,
                None,
                None,
                None,
                None,
                marked_for_deletion)
            flash_result(result)
            return redirect(url_for('dash.dashboard'))
        
    #Checks if edit details was selected, not every field needs to be edited  at the same time 
        elif form_type == 'edit':
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

            flash_result(result)
            return redirect(url_for('dash.dashboard' if result.success else 'auth.edit_user'))

    return render_template('edit_user.html')

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    """POST route to log out the user and return to the login page """
    result = user_service.user_logout()
    flash_result(result)
    return redirect(url_for('auth.login'))