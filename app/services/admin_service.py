from app.models import Genre, User
from app.utils import Result
from app.services.validators import validate_non_empty_string
import logging
from app.services.validators import validate_length


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
        user = User.get_by_id(self.db_session, user_id)
        if user:
            return Result(True, "User found", user)
        else:
            return Result(False, "User not found", None)


    def update_user_role(self, user_id, role):
        try:
            if role not in ('admin', 'regular'):
                return Result(False, "Invalid role type.")

            result = self.get_user_by_id(user_id)
            if not result.success:
                return Result(False, "User not found.")

            user = result.data

            if user.role == 'admin' and role != 'admin':
                admin_count = User.count_admins(self.db_session)
                if admin_count <= 1:
                    # Can't demote last admin
                    return Result(False,
                        "Failed to update user role. You cannot remove admin rights from the last remaining admin. Please promote another user to admin first.",
                        "danger")

            user.role = role
            user.save(self.db_session)
            return Result(True, "User role updated successfully.")

        except Exception as e:
            logging.error(f"An unexpected error occurred while updating user role for user ID {user_id}: {str(e)}")
            return Result(False, f"An error occurred: {str(e)}")


    def delete_record(self, model_class, record_id):
        try:
            record = self.db_session.get(model_class, record_id)
            if not record:
                return Result(False, "Record not found.")

            if model_class == User:
                if record.role == 'admin':
                    admin_count = User.count_admins(self.db_session)
                    if admin_count <= 1:
                        return Result(False,
                                    "Cannot delete the last remaining admin. Please appoint another admin first.")

            record.delete(self.db_session)
            return Result(True, "Record deleted successfully")
        except Exception as e:
            logging.error(f"Error deleting record ID {record_id} of type {model_class.__name__}: {str(e)}")
            return Result(False, f"An error occurred: {str(e)}")

    def create_genre(self, name, image):
        try:
            name = validate_non_empty_string(name, "Genre name")
            error = validate_length(name, "Genre name", 20)
            if error:
                return Result(False, error)
        except ValueError as e:
            return Result(False, str(e))

        existing_genre = Genre.exists_by_name(self.db_session, name)
        if existing_genre:
            return Result(False, "This genre already exists")

        new_genre = Genre(
            name=name,
            image=image,
        )
        try:
            new_genre.save(self.db_session)
            return Result(True, "Genre created successfully")
        except Exception as e:
            logging.error(f"Error creating genre '{name}': {str(e)}")
            return Result(False, f"An error occurred: {str(e)}")

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
            error = validate_length(name, "Genre name", 20)
            if error:
                return Result(False, error)
        except ValueError as e:
            return Result(False, str(e))

        if image is None:
            return Result(False, "Please select an image for the genre.")

        genre.name = name
        genre.image = image
        try:
            genre.save(self.db_session)
            return Result(True, "Genre updated successfully")
        except Exception as e:
            logging.error(f"Error updating genre ID {genre_id}: {str(e)}")
            return Result(False, f"An error occurred: {str(e)}")
