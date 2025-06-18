from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from utils import Result
from extensions import db
from flask_login import logout_user


def register_user(form):
    

    username = form.get('username')
    password = form.get('password')
    re_password = form.get('re_password')
    user_type = form.get('user_type')
    
    if not username or not password or not re_password:
        return Result(False, "All fields are required.")
    
    if password != re_password:
        return Result(False, "Passwords do not match!")
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return Result(False, "username already taken")
    
    new_user = User(username=username, role=user_type)
    new_user.set_password(password)


    db.session.add(new_user)
    db.session.commit()

    return Result(True)

def user_login(form):

    username = form.get('username')
    password = form.get('password')

    if not username or not password:
        return Result(False, "All fields are required.")
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.verify_password(password):
        return Result(True, "Successful login", existing_user)
    else:
        return Result(success=False, message="Invalid username or password")
        
def update_user(user: User, new_username: str, old_password: str, new_password: str, confirm_password: str, marked_for_deletion=None ):
    changes_made = False

    if new_username and new_username != user.username:
        existing_user = User.query.filter_by(username=new_username).first()
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

    marked = (marked_for_deletion == 'yes')
    deletion_requested = None
    if marked != user.marked_for_deletion:
        user.marked_for_deletion = marked
        changes_made = True
        deletion_requested = marked

    db.session.commit()
    
    if not changes_made:
        return Result(False, "No changes made")

    if deletion_requested is True:
        return Result(True, "Account deletion requested. An admin will review your request")
    elif deletion_requested is False:
        return Result(True, "Account deletion has been cancelled.")
    else:
        return Result(True, "Details updated successfully")
    
def user_logout():
    logout_user()
    return Result(True, "You have been logged out")

    
            
        

    




    
