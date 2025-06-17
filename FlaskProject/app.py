from flask import Flask
from extensions import db, login_manager
import os
from routes.auth import auth
from routes.dashboard import dash
from routes.listings import listings
from routes.admin import admin
from models import User
from dotenv import load_dotenv
import sqlite3
from models import User, Loan, Listing, Genre
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



load_dotenv()


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get('SECRET_KEY')
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///bookshare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()


    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth)
    app.register_blueprint(dash)
    app.register_blueprint(listings)
    app.register_blueprint(admin)
    return app