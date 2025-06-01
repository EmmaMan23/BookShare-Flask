from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from services import user_service

auth = Blueprint('auth', __name__)



@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        form_data = request.form
        #print("Received POST:", form_data)
        result = user_service.register_user(form_data)

        if result.success:
            flash("Registration successful, please log in", "success")
            return redirect(url_for('auth.login'))
        else:
            flash(result.message, "danger")
            return render_template('login.html') #keep showing register form if registration failed
        
    return render_template('login.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    return render_template('login.html')


