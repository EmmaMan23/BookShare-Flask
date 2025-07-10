from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# create a single database instance 
db = SQLAlchemy()

#Create a loginManager instance to handle session management and authentication 
login_manager = LoginManager()
