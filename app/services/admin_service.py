from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Genre, Listing, User
from app.services import listing_service
from datetime import date, timedelta
from app.extensions import db
from app.utils import Result
from app.services.validators import validate_non_empty_string
import json
import os


class AdminService:

    metrics_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "metrics.json"))

    def __init__(self, db_session):
        self.db_session = db_session
    
    def view_users(self):
        users = self.db_session.query(User).all()
        return Result(True, "Users retrieved successfully", users)
    
    
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
        genres = self.db_session.query(Genre).all()
        return Result(True, "Genres returned successfully", genres)
    
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
    
    def metrics(self):
    
        with open(self.metrics_file, "r") as f:
            data = json.load(f)
        print(data)
        return data
        

