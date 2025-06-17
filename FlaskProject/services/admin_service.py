from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from models import Genre, Listing, User
from services import listing_service
from datetime import date, timedelta

def view_users():
    return User.query.all()