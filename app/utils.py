from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


class Result:
    """ Represents the result of an operation """
    def __init__(self, success, message=None, data=None):
        self.success = success
        self.message = message
        self.data = data

def flash_result(result: Result):
    """Flash message helper, sets the status of the side-effects to success or danger """
    flash(result.message, "success" if result.success else "danger")


def admin_required(f):
    """Decorator to restrict certain pages to admins only """
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
