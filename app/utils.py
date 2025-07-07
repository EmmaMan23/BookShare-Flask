from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


class Result:
    def __init__(self, success, message=None, data=None):
        self.success = success
        self.message = message
        self.data = data


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.")
            return redirect(url_for('login'))

        if not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for('dash.dashboard'))

        return f(*args, **kwargs)
    return decorated_function
