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
        form_data = request.form
        name = form_data.get('name')
        image = form_data.get('image')
        inactive = False
        admin_service.create_genre(name, image, inactive)
        return redirect(url_for('admin.create_genre'))
        
    genres = admin_service.get_genres()
    return render_template('add_genre.html', genre_images=genre_images, genres=genres)

@admin.route('/edit_genre', methods=['POST'])

def edit_genre():
    form_data = request.form
    genre_id = form_data.get('id')
    name = form_data.get('name')
    image = form_data.get('image')

    updated_genre = admin_service.edit_genre(genre_id, name, image)

    if not updated_genre:
        flash("Genre not found or missing data.", "danger")

    else:
        flash("Genre updated successfully!", "success")

    return redirect(url_for('admin.create_genre'))


    
    
    