from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash, session
from services import user_service
from flask_login import login_user, logout_user

auth = Blueprint('auth', __name__)




@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        form_data = request.form
        result = user_service.register_user(form_data)

        if result.success:
            flash("Registration successful, please log in", "success")
            return redirect(url_for('auth.login'))
        else:
            flash(result.message, "danger")
            return render_template('login.html', show_register=True) #keep showing register form if registration failed
        
    return render_template('login.html', show_register=False)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form_data = request.form
        result = user_service.authenticate_user(form_data)

        if result.success:
            login_user(result.data)
            flash("Successful login", "success")
            return redirect(url_for('dash.dashboard'))
        else:
            flash(result.message, "danger")
            return render_template('login.html', show_register=False)
        
    return render_template('login.html', show_register=False)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect('login')
