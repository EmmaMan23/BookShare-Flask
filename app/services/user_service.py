from werkzeug.security import generate_password_hash
from app.models import User
from app.utils import Result
from flask_login import logout_user
from app.services.validators import validate_non_empty_string
from datetime import date
import os


class UserService:
    def __init__(self, db_session):
        self.db_session = db_session

    def _validate_username(self, username):
        try:
            valid_username = validate_non_empty_string(username, "Username").lower()
            return Result(True, data=valid_username)
        except ValueError as e:
            return Result(False, str(e))


    def _validate_password(self, password, field_name="Password"):
        try:
            valid_password = validate_non_empty_string(password, field_name)
            return Result(True, data=valid_password)
        except ValueError as e:
            return Result(False, str(e))


    def register_user(self, username, password, re_password, user_type, admin_code):
        username_result = self._validate_username(username)
        if not username_result.success:
            return username_result
        username = username_result.data


        password_result = self._validate_password(password)
        if not password_result.success:
            return password_result
        password = password_result.data


        re_password_result = self._validate_password(re_password)
        if not re_password_result.success:
            return re_password_result
        re_password = re_password_result.data


        if password != re_password:
            return Result(False, "Unsuccessful registration, Passwords need to match!")

        if user_type == "admin":
            admin_code_env = os.getenv('ADMIN_CODE')
            if admin_code != admin_code_env:
                return Result(False, "Invalid admin registration code!")

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
        username_result = self._validate_username(username)
        if not username_result.success:
            return username_result
        username = username_result.data

        password_result = self._validate_password(password)
        if not password_result.success:
            return password_result
        password = password_result.data

        existing_user = User.existing_user(self.db_session, username)
        if existing_user and existing_user.verify_password(password):
            return Result(True, "Successful login", existing_user)
        else:
            return Result(False, "Invalid username or password")


    def update_user(self, user: User, new_username: str, old_password: str, new_password: str, confirm_password: str, marked_for_deletion=None):
        changes_made = False

        if new_username is not None and new_username != user.username:
            username_result = self._validate_username(new_username)
            if not username_result.success:
                return username_result
            new_username = username_result.data

            existing_user = User.existing_user(self.db_session, new_username)
            if existing_user:
                return Result(False, "Username already taken")

            user.username = new_username
            changes_made = True

        if old_password or new_password or confirm_password:
            if not all([old_password, new_password, confirm_password]):
                return Result(False, "All fields required to change password")

            if not user.verify_password(old_password):
                return Result(False, "Current Password entered incorrectly")

            new_password_result = self._validate_password(new_password, "New Password")
            if not new_password_result.success:
                return new_password_result
            new_password = new_password_result.data

            confirm_result = self._validate_password(confirm_password, "Confirm Password")
            if not confirm_result.success:
                return confirm_result
            confirm_password = confirm_result.data

            if new_password != confirm_password:
                return Result(False, "New password and confirmation password do not match!")

            user.password_hash = generate_password_hash(new_password)
            changes_made = True

        # ✅ Unchanged: deletion logic preserved as requested
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

        if deletion_requested is True:
            return Result(True, "Account deletion requested. An admin will review your request")
        elif deletion_requested is False:
            return Result(True, "Account deletion has been cancelled")
        else:
            return Result(True, "Details updated successfully")


    def user_logout(self):
        logout_user()
        return Result(True, "You have been logged out")
