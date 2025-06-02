#from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from utils import Result
from extensions import db


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
        

    




    
