from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from models import Genre, Listing, User, Loan
from services.admin_service import AdminService
from extensions import db


admin_service = AdminService(db.session)

admin = Blueprint('admin', __name__)

@admin.route('/view_users')
def view_users():
    user_data = admin_service.view_users()
    return render_template('view_users.html', users=user_data)

@admin.route('/delete_record', methods=['POST'])
def delete():
    data = request.form

    model = data.get('model')
    record_id = data.get('id')

    model_map ={
        'user': User,
        'listing': Listing,
        'genre': Genre,
        'loan': Loan
    }

    model_class = model_map.get(model.lower())
    admin_service.delete_record(model_class, int(record_id))

    return redirect(url_for('listings.view_all'))

@admin.route('/create_genre', methods=['POST', 'GET'])
def create_genre():
    form_data = request.form

    genre_images = [
        'images/adventure.png',
        'images/children.png',
        'images/fantasy.png',
        'images/horror.png',
        'images/mystery.png',
        'images/romance.png',
        'images/science.png',
    ]
    if request.method == 'POST':
        admin_service.create_genre(form_data)
        return render_template('view_users.html')
        

    return render_template('add_genre.html', genre_images=genre_images)