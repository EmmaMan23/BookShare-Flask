from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from models import Genre, Listing, User
from services import listing_service
from datetime import date, timedelta
from extensions import db

class AdminService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def view_users(self):
        return User.query.all()
    
    def delete_record(self, model_class,  record_id):
        record = model_class.query.get(record_id)
        if not record:
            return False #Record not found

        self.db_session.delete(record)
        self.db_session.commit()
        return True

    def create_genre(self, name, image, inactive):
        

        new_genre = Genre(
            name = name,
            image = image,
            inactive = inactive
        )

        db.session.add(new_genre)
        db.session.commit()

    def get_genres(self):
        return Genre.query.all()
    
    def edit_genre(self, genre_id, name, image):
        
        if not genre_id:
            return None
        
        genre = Genre.query.get(genre_id)
        if not genre:
            return None
        
        genre.name = name
        genre.image = image 
        db.session.commit()

