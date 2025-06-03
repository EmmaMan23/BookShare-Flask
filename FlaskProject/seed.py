from extensions import db
from models import User, Genre
from werkzeug.security import generate_password_hash
from app import create_app

app = create_app()


with app.app_context():

    genres = [
        {
        "name": "Science Fiction",
        "image": "images/science.png",
        "marked_for_deletion": False
        },
        {"name": "Fantasy"},
        {"name": "Romance"},
        {"name": "Horror"},
        {"name": "Mystery"},
        {"name": "Thriller"},
        {"name": "History"},
        {"name": "Non-Fiction"},
        {"name": "Biography"},
        {"name": "Children"}
    ]


    users = [
        {
            "username": "Clive",
            "password": "Shoes123",
            "role": "admin",
            "marked_for_deletion": False
        }
    ]

    for i in users:
        hashed_password = generate_password_hash(i["password"])
        user = User(
            username = i["username"],
            password_hash = hashed_password,
            role = i["role"],
            marked_for_deletion = i["marked_for_deletion"]
        )

        db.session.add(user)
    db.session.commit()