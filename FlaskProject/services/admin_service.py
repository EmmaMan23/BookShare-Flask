from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from models import Genre, Listing, User
from services import listing_service
from datetime import date, timedelta
from extensions import db
from utils import Result
from .validators import validate_non_empty_string

class AdminService:
    def __init__(self, db_session):
        self.db_session = db_session
    
    def view_users(self):
        return self.db_session.query(User).all()
    
    def delete_record(self, model_class, record_id):
        record = self.db_session.get(model_class, record_id)
        if not record:
            return Result(False, "Record not found.")

        self.db_session.delete(record)
        self.db_session.commit()
        return Result(True, "Record deleted successfully")

    def create_genre(self, name, image, inactive):
        try:
            name = validate_non_empty_string(name, "Genre name")
        except ValueError as e:
            return Result(False, str(e))

        new_genre = Genre(
            name = name,
            image = image,
            inactive = inactive
        )

        self.db_session.add(new_genre)
        self.db_session.commit()
        return Result(True, "Genre created successfully")

    def get_genres(self):
        return self.db_session.query(Genre).all()
    
    def edit_genre(self, genre_id, name, image):
        
        if not genre_id:
            return Result(False, "No genre ID provided.")
        
        genre = self.db_session.get(Genre, genre_id)
        if not genre:
            return Result(False, "Genre not found.")
        
        try:
            name = validate_non_empty_string(name, "Genre name")
        except ValueError as e:
            return Result(False, str(e))
        
        genre.name = name
        genre.image = image 
        self.db_session.commit()
        return Result(True, "Genre updated successfully")

