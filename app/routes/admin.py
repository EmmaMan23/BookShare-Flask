from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Genre, Listing, User, Loan
from app.services.admin_service import AdminService
from app.services.listing_service import ListingService
from app.services.dashboard_service import DashboardService
from app.extensions import db

dashboard_service = DashboardService(db.session, "app/static/metrics.json")
admin_service = AdminService(db.session)
listing_service = ListingService(db.session, dashboard_service)

admin = Blueprint('admin', __name__)

@admin.route('/view_users')
@login_required
def view_users():
    args = request.args
    sort_join_date = args.get('sort_join_date', 'desc')
    filter_role = args.get('filter_role')  
    marked_for_deletion = args.get('marked_for_deletion')
    search = args.get('search')

    if sort_join_date not in ('asc', 'desc'):
        sort_join_date = 'desc'

    user_result = admin_service.view_users(
        search=search,
        sort_join_date=sort_join_date,
        filter_role=filter_role,
        marked_for_deletion=marked_for_deletion
    )
    data = dashboard_service.read_metrics(current_user)
    return render_template(
        'view_users.html',
        users=user_result.data,
        metrics=data,
        search=search,
        sort_join_date=sort_join_date,
        role=filter_role,
        marked_for_deletion=marked_for_deletion
        )


@admin.route('/delete_record', methods=['POST'])
@login_required
def delete():
    if not current_user.is_admin:
        flash("Unauthorised: Admins only", "danger")
        return redirect(url_for('dash.dashboard'))
    
    form_data = request.form

    model = form_data.get('model')
    record_id = form_data.get('id')

    model_map = {
        'user': User,
        'listing': Listing,
        'genre': Genre,
        'loan': Loan
    }

    model_class = model_map.get(model.lower())
    if not model_class:
        flash("Invalid model type.", "danger")
        return redirect(url_for('listings.view_all'))

    # Determine redirect scope if loan
    loan_user_id = None
    if model_class == Loan:
        loan_result = listing_service.get_loan_by_id(int(record_id))
        if loan_result.success:
            loan_obj = loan_result.data
            loan_user_id = loan_obj.user_id
        else:
            flash("Loan not found.", "danger")
            return redirect(url_for('listings.view_loans', scope='all'))

    result = admin_service.delete_record(model_class, int(record_id))
    flash(result.message, "success" if result.success else "danger")

    # Redirect based on model
    if model_class == User:
        return redirect(url_for('admin.view_users'))
    elif model_class == Genre:
        kind = "genre"
        return redirect(url_for('admin.create_genre', kind=kind))
    elif model_class == Loan:
        scope = 'self' if loan_user_id == current_user.user_id else 'all'
        return redirect(url_for('listings.view_loans', scope=scope))
    else:
        return redirect(url_for('listings.view_all'))



@admin.route('/create_genre', methods=['POST', 'GET'])
@login_required
def create_genre():
    listing_service = ListingService(db.session, dashboard_service)
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
        name = form_data.get('name').strip().capitalize()
        image = form_data.get('image')
        request.form.get("image")

        if not image:
            flash("Unsuccessful, please select an image when creating a genre.", "danger")
            return redirect(url_for('admin.create_genre'))


        result = admin_service.create_genre(name, image)
        flash(result.message, "success" if result.success else "danger")
        return redirect(url_for('admin.create_genre'))
        
    genres_result = listing_service.get_all_genres()
    return render_template('add_genre.html', genre_images=genre_images, genres=genres_result)

@admin.route('/edit_genre', methods=['POST'])
@login_required
def edit_genre():
    form_data = request.form
    genre_id = form_data.get('id')
    name = form_data.get('name', '').strip().capitalize()
    image = form_data.get('image')

    result = admin_service.edit_genre(genre_id, name, image)

    
    flash(result.message, "success" if result.success else "danger")
    return redirect(url_for('admin.create_genre'))

@admin.route('/admin_edit_user', methods=['GET', 'POST'])
@login_required
def admin_edit_user():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        flash("User ID is missing.", "danger")
        return redirect(url_for('admin.view_users'))
    
    user = admin_service.get_user_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.view_users'))

    if request.method == 'POST':
        role = request.form.get('role')

        result = admin_service.update_user_role(user_id, role)
        flash(result.message, "success" if result.success else "danger")

        if result.success:
            return redirect(url_for('admin.view_users'))
        else:
            users_result = admin_service.view_users()
            users = users_result.data if users_result.success else []
            return render_template('view_users.html', users=users, user=user)
    
    return render_template('view_users.html', user=user)
