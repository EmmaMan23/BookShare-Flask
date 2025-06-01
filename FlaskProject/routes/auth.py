from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from services import user_service

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
        result = user_service.login_user(form_data)

        if result.success:
            flash("Successful login", "success")
            return redirect(url_for('dash.dashboard'))
        else:
            flash(result.message, "danger")
            return render_template('login.html', show_register=False)
        
    return render_template('login.html', show_register=False)


