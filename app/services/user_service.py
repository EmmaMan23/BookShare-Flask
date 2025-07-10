from werkzeug.security import generate_password_hash
from app.models import User
from app.utils import Result
from flask_login import logout_user
from app.services.validators import validate_non_empty_string, validate_length
from datetime import date
import os


class UserService:
    def __init__(self, db_session):
        self.db_session = db_session

    def _validate_username(self, username):
        """Validates the username is a non-empty string, ensures data type is correct"""
        try:
            valid_username = validate_non_empty_string(username, "Username").lower()
            return Result(True, data=valid_username)
        except ValueError as e:
            return Result(False, str(e))


    def _validate_password(self, password, field_name="Password"):
        """Validates the password is a non-empty string, ensures data type is correct"""
        try:
            valid_password = validate_non_empty_string(password, field_name)
            return Result(True, data=valid_password)
        except ValueError as e:
            return Result(False, str(e))


    def register_user(self, username, password, re_password, user_type, admin_code):
        """Registers a new user after validating credentials """

        # Validate username length (max 30)
        length_error = validate_length(username, "Username", 30)
        if length_error:
            return Result(False, length_error)

        username_result = self._validate_username(username)
        if not username_result.success:
            return username_result
        username = username_result.data

        # Validate password length (max 255)
        length_error = validate_length(password, "Password", 255)
        if length_error:
            return Result(False, length_error)

        password_result = self._validate_password(password)
        if not password_result.success:
            return password_result
        password = password_result.data

        # Validate re_password length (max 255)
        length_error = validate_length(re_password, "Confirm Password", 255)
        if length_error:
            return Result(False, length_error)

        re_password_result = self._validate_password(re_password)
        if not re_password_result.success:
            return re_password_result
        re_password = re_password_result.data

        #Check if passwords match
        if password != re_password:
            return Result(False, "Unsuccessful registration, Passwords need to match!")

        #If the new user is an admin verify the admin_code
        if user_type == "admin":
            admin_code_env = os.getenv('ADMIN_CODE')
            if admin_code != admin_code_env:
                return Result(False, "Invalid admin registration code!")

        #Check the username is unique
        existing_user = User.existing_user(self.db_session, username)
        if existing_user:
            return Result(False, "Username already taken")

        new_user = User(
            username=username,
            role=user_type,
            join_date=date.today(),
            total_loans=0,
            total_listings=0
        )
        new_user.set_password(password)

        try:
            new_user.save(self.db_session)
        except Exception as e:
            return Result(False, f"Failed to register user: {str(e)}")

        return Result(True, "Registration successful, please log in")


    def user_login(self, username, password):
        """Authenticate the user credentials and return the user if valid """

        # Validate username length (max 30)
        length_error = validate_length(username, "Username", 30)
        if length_error:
            return Result(False, length_error)

        username_result = self._validate_username(username)
        if not username_result.success:
            return username_result
        username = username_result.data

        # Validate password length (max 255)
        length_error = validate_length(password, "Password", 255)
        if length_error:
            return Result(False, length_error)

        password_result = self._validate_password(password)
        if not password_result.success:
            return password_result
        password = password_result.data

        # Verify user existence and password correctness
        existing_user = User.existing_user(self.db_session, username)
        if existing_user and existing_user.verify_password(password):
            return Result(True, "Successful login", existing_user)
        else:
            return Result(False, "Invalid username or password")



    def update_user(self, user: User, new_username: str, old_password: str, new_password: str, confirm_password: str, marked_for_deletion=None):
        """Update user details - Username, password and mark for delete status """

        changes_made = False

        #Update username is changes are made 
        if new_username is not None and new_username != user.username:
            length_error = validate_length(new_username, "Username", 30)
            if length_error:
                return Result(False, length_error)

            username_result = self._validate_username(new_username)
            if not username_result.success:
                return username_result
            new_username = username_result.data

            #Check username is not taken
            existing_user = User.existing_user(self.db_session, new_username)
            if existing_user:
                return Result(False, "Username already taken")

            user.username = new_username
            changes_made = True

        #Update password if changes are made 
        if old_password or new_password or confirm_password:
            if not all([old_password, new_password, confirm_password]):
                return Result(False, "All fields required to change password")

            #Verify old password matches
            if not user.verify_password(old_password):
                return Result(False, "Current Password entered incorrectly")

            #Validate password length
            length_error = validate_length(new_password, "New Password", 255)
            if length_error:
                return Result(False, length_error)

            new_password_result = self._validate_password(new_password, "New Password")
            if not new_password_result.success:
                return new_password_result
            new_password = new_password_result.data

            #Validate confirm password length 
            length_error = validate_length(confirm_password, "Confirm Password", 255)
            if length_error:
                return Result(False, length_error)

            confirm_result = self._validate_password(confirm_password, "Confirm Password")
            if not confirm_result.success:
                return confirm_result
            confirm_password = confirm_result.data

            #Check if new password and confirm passwords match 
            if new_password != confirm_password:
                return Result(False, "New password and confirmation password do not match!")

            #Hash the password for the database
            user.password_hash = generate_password_hash(new_password)
            changes_made = True

        #Handle the marked_for_deletion toggle logic 
        deletion_requested = None
        if marked_for_deletion in ['true', 'on', '1', True]:
            if user.marked_for_deletion != True:
                user.marked_for_deletion = True
                deletion_requested = True
            else:
                user.marked_for_deletion = False
                deletion_requested = False
            changes_made = True

        try:
            user.save(self.db_session)
        except Exception as e:
            return Result(False, f"Failed to update user: {str(e)}")

        if not changes_made:
            return Result(False, "No changes made")

        #Return messages based on the mark for deletion statu
        if deletion_requested is True:
            return Result(True, "Account deletion requested. An admin will review your request")
        elif deletion_requested is False:
            return Result(True, "Account deletion has been cancelled")
        else:
            return Result(True, "Details updated successfully")


    def user_logout(self):
        """Log out the currently logged in user """
        logout_user()
        return Result(True, "You have been logged out")
