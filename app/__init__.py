from flask import Flask
from app.extensions import db, login_manager
import os
from app.routes.auth import auth
from app.routes.dashboard import dash
from app.routes.listings import listings
from app.routes.admin import admin
from app.models import User
from dotenv import load_dotenv
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

# Enable foreign key constraints in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Load environment variables from a .env file
load_dotenv()

# Set up logging for error tracking
logging.basicConfig(filename='app.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s: %(message)s')


def create_app(testing=False):

    # Create Flask app instance and specify static folder location
    app = Flask(__name__, static_folder='static')

    # Set secret key (used for session management)
    app.secret_key = os.environ.get('SECRET_KEY', 'testing_secret_key')

    # Configure database based on whether testing or running normally
    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///bookshare.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialise the database with the Flask app
    db.init_app(app)

    # Create all database tables within the app context
    with app.app_context():
        db.create_all()

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    # Load the current user from the database by ID
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register route blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dash)
    app.register_blueprint(listings)
    app.register_blueprint(admin)

    return app
