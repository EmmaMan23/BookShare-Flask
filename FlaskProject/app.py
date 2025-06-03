from flask import Flask
from extensions import db, login_manager
import os
from routes.auth import auth
from routes.dashboard import dash
from models import User
from dotenv import load_dotenv
import sqlite3
from models import User, Loan, Listing, Genre

load_dotenv()

# user = os.environ.get("MYSQL_USER")
# password = os.environ.get("MYSQL_PASSWORD")
# host = os.environ.get("MYSQL_HOST")
# database = os.environ.get('MYSQL_DB')
# port = os.environ.get("MYSQL_PORT")




def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get('SECRET_KEY')
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///bookshare.db'
    #f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth)
    app.register_blueprint(dash)
    return app