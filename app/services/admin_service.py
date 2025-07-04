from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash
from app.models import Genre, Listing, User
from app.services import listing_service
from datetime import date, timedelta
from app.extensions import db
from app.utils import Result
from app.services.validators import validate_non_empty_string
import json
import os
from sqlalchemy import func
import logging


class AdminService:

    def __init__(self, db_session):
        self.db_session = db_session
    
    def view_users(self, search=None, sort_join_date='desc', filter_role=None, marked_for_deletion=None):

        users = User.filter_search_query(
            db_session=self.db_session,
            search=search,
            filter_role=filter_role,
            marked_for_deletion=marked_for_deletion,
            sort_join_date=sort_join_date
        )

        return Result(True, "Users retrieved successfully", users)


    def get_user_by_id(self, user_id):
        return User.get_by_id(self.db_session, user_id)

    def update_user_role(self, user_id, role):
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return Result(False, "User not found.")

            if user.role == 'admin' and role != 'admin':
                        admin_count = User.count_admins(self.db_session)
                        if admin_count <= 1:
                            # Can't demote last admin
                            return Result(False, "Failed to update user role. You cannot remove admin rights from the last remaining admin. Please promote another user to admin first", "danger")
            user.role = role
            user.save(self.db_session)
            return Result(True, "User role updated successfully.")
        
        except Exception as e:
            self.db_session.rollback()
            logging.error(f"An unexpected error occurred while updating user role for user ID {user_id}: {str(e)}")
            return Result(False, f"An error occurred: {str(e)}")

    
    def delete_record(self, model_class, record_id):
        record = self.db_session.get(model_class, record_id)
        if not record:
            return Result(False, "Record not found.")
        if model_class == User:

            if record.role == 'admin':
                admin_count = User.count_admins(self.db_session)
                if admin_count <= 1:
                    return Result(False, "Cannot delete the last remaining admin. Please appoint another admin first.")

        record.delete(self.db_session)
        return Result(True, "Record deleted successfully")

    def create_genre(self, name, image):
        try:
            name = validate_non_empty_string(name, "Genre name")
        except ValueError as e:
            return Result(False, str(e))
        
        existing_genre = Genre.exists_by_name(self.db_session, name)
        if existing_genre:
            return Result(False, "This genre already exists")

        new_genre = Genre(
            name = name,
            image = image,
        )

        new_genre.save(self.db_session)
        return Result(True, "Genre created successfully")
    
    def edit_genre(self, genre_id, name, image):
        
        if not genre_id:
            return Result(False, "No genre ID provided.")
        
        try:
            genre_id = int(genre_id)
        except (ValueError, TypeError):
            return Result(False, "Invalid genre ID.")

        
        genre = Genre.get_by_id(self.db_session, genre_id)
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
        genre.save(self.db_session)
        return Result(True, "Genre updated successfully")
    
    
        

