from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash

dash = Blueprint('dash', __name__)

@dash.route('/dashboard')
def dashboard():
    return("Hello dashbaord")