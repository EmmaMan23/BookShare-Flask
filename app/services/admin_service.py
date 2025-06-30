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


    def __init__(self, db_session):
        self.db_session = db_session
    
    def view_users(self):
        users = self.db_session.query(User).all()
        return Result(True, "Users retrieved successfully", users)
    
    
    def get_user_by_id(self, user_id):
        return self.db_session.query(User).filter_by(user_id=user_id).first()

    def update_user_role(self, user_id, role):
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return Result(False, "User not found.")

            if user.role == 'admin' and role != 'admin':
                        admin_count = self.db_session.query(User).filter_by(role='admin').count()
                        if admin_count <= 1:
                            # Can't demote last admin
                            return Result(False, "Failed to update user role. You cannot remove admin rights from the last remaining admin. Please promote another user to admin first", "danger")
            user.role = role
            self.db_session.commit()
            return Result(True, "User role updated successfully.")
        
        except Exception as e:
            self.db_session.rollback()
            return Result(False, f"An error occurred: {str(e)}")

    
    def delete_record(self, model_class, record_id):
        record = self.db_session.get(model_class, record_id)
        if not record:
            return Result(False, "Record not found.")
        if model_class == User:

            if record.role == 'admin':
                remaining_admins = self.db_session.query(User).filter(
                    User.role == 'admin',
                    User.user_id != record.user_id
                ).count()
                if remaining_admins == 0:
                    return Result(False, "Cannot delete the last remaining admin. Please appoint another admin first.")

        self.db_session.delete(record)
        self.db_session.commit()
        return Result(True, "Record deleted successfully")

    def create_genre(self, name, image):
        try:
            name = validate_non_empty_string(name, "Genre name")
        except ValueError as e:
            return Result(False, str(e))

        new_genre = Genre(
            name = name,
            image = image,
        )

        self.db_session.add(new_genre)
        self.db_session.commit()
        return Result(True, "Genre created successfully")
    
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
        
        if not image:
            return Result(False, "Please select an image for the genre.")
    
        genre.name = name
        genre.image = image 
        self.db_session.commit()
        return Result(True, "Genre updated successfully")
    
    
        

