from app.models import Genre, User
from app.utils import Result
from app.services.validators import validate_non_empty_string
import logging
from app.services.validators import validate_length


class AdminService:

    def __init__(self, db_session):
        #Dependency injection of the database session 
        self.db_session = db_session

    def view_users(self, search=None, sort_join_date='desc', filter_role=None, marked_for_deletion=None):
        """Retrieves a list of users with optional filtering, sorting, and search"""
        users = User.filter_search_query(
            db_session=self.db_session,
            search=search,
            filter_role=filter_role,
            marked_for_deletion=marked_for_deletion,
            sort_join_date=sort_join_date
        )
        return Result(True, "Users retrieved successfully", users)

    def get_user_by_id(self, user_id):
        """Retrieves users by their ID"""
        user = User.get_by_id(self.db_session, user_id)
        if user:
            return Result(True, "User found", user)
        else:
            return Result(False, "User not found", None)


    def update_user_role(self, user_id, role):
        """Updates the role of a user.
        Prevents demoting the last remaining admin """

        try:
            if role not in ('admin', 'regular'):
                return Result(False, "Invalid role type.")
            
            #Checks user exists 
            result = self.get_user_by_id(user_id)
            if not result.success:
                return Result(False, "User not found.")

            user = result.data

            # Prevents the demotion of the last admin
            if user.role == 'admin' and role != 'admin':
                admin_count = User.count_admins(self.db_session)
                if admin_count <= 1:
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
        """Deletes a record (User, Loan, Listing, Genre) of the specified model by ID.
        Prevents deleting the last admin"""

        try:
            record = self.db_session.get(model_class, record_id)
            if not record:
                return Result(False, "Record not found.")

            #If deleting a user, check it is not the last admin
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
        """Creates a new genre after validating input, 
        Ensures name is unique and within character limits"""

        try:
            #Validate name
            name = validate_non_empty_string(name, "Genre name")
            error = validate_length(name, "Genre name", 20)
            if error:
                return Result(False, error)
        except ValueError as e:
            return Result(False, str(e))
        
        #Check the genre name is unique
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
        """Edits an existing genre's name and image after validating input"""

        if not genre_id:
            return Result(False, "No genre ID provided.")

        #Validate the genre ID is an integer
        try:
            genre_id = int(genre_id)
        except (ValueError, TypeError):
            return Result(False, "Invalid genre ID.")
        
        genre = Genre.get_by_id(self.db_session, genre_id)
        if not genre:
            return Result(False, "Genre not found.")
        
        #Validate the name for length
        try:
            name = validate_non_empty_string(name, "Genre name")
            error = validate_length(name, "Genre name", 20)
            if error:
                return Result(False, error)
        except ValueError as e:
            return Result(False, str(e))
        
        # Check the genre name is unique (excluding this genre)
        if Genre.exists_by_name_excluding_id(self.db_session, name, genre_id):
            return Result(False, "This genre already exists")

        #Ensure an image is selected
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
