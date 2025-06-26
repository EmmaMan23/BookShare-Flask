from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app.utils import Result
from app.extensions import db
from flask_login import logout_user
from app.services.validators import validate_non_empty_string
from datetime import date



class UserService:
    def __init__(self, db_session):
        self.db_session = db_session

    def register_user(self, username, password, re_password, user_type, admin_code):
        
        try:
            username = validate_non_empty_string(username, "Username").lower()
            password = validate_non_empty_string(password, "Password")
            re_password = validate_non_empty_string(re_password, "Password Confirmation")
            join_date = date.today()
            total_loans = 0
            total_listings = 0
        except ValueError as e:
            return Result(False, str(e))
        
        if password != re_password:
            return Result(False, "Passwords do not match!")

        if user_type == "admin":
            if admin_code != "Secretadmin3":
                return Result(False, "Invalid admin registration code!")
            
        existing_user = self.db_session.query(User).filter_by(username=username).first()
        if existing_user:
            return Result(False, "Username already taken")
            
        new_user = User(username=username, role=user_type, join_date=join_date, total_loans=total_loans, total_listings=total_listings)
        new_user.set_password(password)


        self.db_session.add(new_user)
        self.db_session.commit()

        return Result(True, "Registration successful")

    def user_login(self, username, password):
        try:
            username = validate_non_empty_string(username, "Username")
            password = validate_non_empty_string(password, "Password")
        except ValueError as e:
            return Result(False, str(e))

        existing_user = self.db_session.query(User).filter_by(username=username).first()
        if existing_user and existing_user.verify_password(password):
            return Result(True, "Successful login", existing_user)
        else:
            return Result(success=False, message="Invalid username or password")
            
    def update_user(self, user: User, new_username: str, old_password: str, new_password: str, confirm_password: str, marked_for_deletion=None ):
        changes_made = False

        if new_username and new_username != user.username:
            try:
                new_username = validate_non_empty_string(new_username, "Username")
            except ValueError as e:
                return Result(False, str(e))


            existing_user = self.db_session.query(User).filter_by(username=new_username).first()
            if existing_user:
                return Result(False, "Username already taken")
            
            user.username = new_username
            changes_made = True

        if old_password or new_password or confirm_password:
            if not all([old_password, new_password, confirm_password]):
                return Result(False, "All fields required to change password")
            if not user.verify_password(old_password):
                return Result(False, "Current Password entered incorrectly")
            if new_password != confirm_password:
                return Result(False, "New password and confirmation password do not match!")
            
            user.password_hash = generate_password_hash(new_password)
            changes_made = True

        deletion_requested = None

        if marked_for_deletion in ['true', 'on', '1', True]:
        
            user.marked_for_deletion = not user.marked_for_deletion
            deletion_requested = user.marked_for_deletion
            changes_made = True


        self.db_session.commit()
        
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

        
                
            

        




        
