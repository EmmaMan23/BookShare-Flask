from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
host = os.environ.get("MYSQL_HOST")
database = os.environ.get('MYSQL_DB')
port = os.environ.get("MYSQL_PORT")

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    return app