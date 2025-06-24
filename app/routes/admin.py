from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Genre, Listing, User, Loan
from app.services.admin_service import AdminService
from app.extensions import db


admin_service = AdminService(db.session)

admin = Blueprint('admin', __name__)

@admin.route('/view_users')
@login_required
def view_users():
    user_result = admin_service.view_users()
    return render_template('view_users.html', users=user_result.data)

@admin.route('/delete_record', methods=['POST'])
@login_required
def delete():
    if not current_user.is_admin:
        flash("Unauthorised: Admins only", "danger")
        return redirect(url_for('dash.dashboard'))
    
    form_data = request.form

    model = form_data.get('model')
    record_id = form_data.get('id')

    model_map ={
        'user': User,
        'listing': Listing,
        'genre': Genre,
        'loan': Loan
    }

    model_class = model_map.get(model.lower())
    if not model_class:
        flash("Invalid model type.", "danger")
        return redirect(url_for('listings.view_all'))
    
    result = admin_service.delete_record(model_class, int(record_id))
    flash(result.message, "success" if result.success else "danger")
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

        result = admin_service.create_genre(name, image, inactive)
        flash(result.message, "success" if result.success else "danger")
        return redirect(url_for('admin.create_genre'))
        
    genres_result = admin_service.get_genres()
    return render_template('add_genre.html', genre_images=genre_images, genres=genres_result.data)

@admin.route('/edit_genre', methods=['POST'])

def edit_genre():
    form_data = request.form
    genre_id = form_data.get('id')
    name = form_data.get('name')
    image = form_data.get('image')

    result = admin_service.edit_genre(genre_id, name, image)

    
    flash(result.message, "success" if result.success else "danger")
    return redirect(url_for('admin.create_genre'))


    
    
    