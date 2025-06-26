from app.extensions import db
from app.models import User, Genre, Listing, Loan
from werkzeug.security import generate_password_hash
from app import create_app
from datetime import date

app = create_app()

def seeding():
    with app.app_context():

        genres = [
            {
            "name": "Science Fiction",
            "image": "images/science.png",
            "inactive": False
            },
            {
            "name": "Fantasy",
            "image": "images/fantasy.png",
            "inactive": False
            },
            {
            "name": "Romance",
            "image": "images/romance.png",
            "inactive": False
            },
            {
            "name": "Horror",
            "image": "images/horror.png",
            "inactive": False
            },
            {
            "name": "Mystery",
            "image": "images/mystery.png",
            "inactive": False
            },
            {
            "name": "Thriller",
            "image": "images/science.png",
            "inactive": False
            },
            {
            "name": "History",
            "image": "images/adventure.png",
            "inactive": False
            },
            {
            "name": "Non-Fiction",
            "image": "images/science.png",
            "inactive": False
            },
            {
            "name": "Adventure",
            "image": "images/adventure.png",
            "inactive": False
            },
            {
            "name": "Children",
            "image": "images/children.png",
            "inactive": False
            }
        ]

        for g in genres:
            genre = Genre(
                name =g["name"],
                image = g["image"],
                inactive = g["inactive"]
            )
            db.session.add(genre)
        db.session.commit()


        users = [
            {
                "username": "clive",
                "password": "Shoes123",
                "role": "admin",
                "marked_for_deletion": False,
                "total_loans": 0,
                "total_listings": 0,
                "join_date": date(2024, 12, 10)

            },
            {
                "username": "sally",
                "password": "Shoes345",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 5,
                "total_listings": 7,
                "join_date": date(2024, 12, 10)
            },
            {
                "username": "john",
                "password": "Cat57",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 4,
                "total_listings": 6,
                "join_date": date(2024, 12, 10)
            },
            {
                "username": "emily",
                "password": "Cats700",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 8,
                "total_listings": 3,
                "join_date": date(2024, 12, 10)
            },
            {
                "username": "sebastian",
                "password": "Dogs",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 9,
                "total_listings": 3,
                "join_date": date(2024, 12, 10)
            },
            {
                "username": "sam",
                "password": "Ducks",
                "role": "admin",
                "marked_for_deletion": False,
                "total_loans": 2,
                "total_listings": 4,
                "join_date": date(2024, 12, 10)
            },
            {
                "username": "sophie",
                "password": "Llamas45",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 5,
                "total_listings": 2,
                "join_date": date(2024, 12, 10)
            },
            {
                "username": "charlie",
                "password": "Piesforever",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans":5 ,
                "total_listings": 1,
                "join_date": date(2024, 12, 10)
            },
            {
                "username": "chantelle",
                "password": "Gingerfluff",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 6,
                "total_listings": 8,
                "join_date": date(2024, 12, 10)
            },
            {
                "username": "nathan",
                "password": "Ilovefootball",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 5 ,
                "total_listings": 1,
                "join_date": date(2024, 12, 10)
            }
        ]

        for i in users:
            hashed_password = generate_password_hash(i["password"])
            user = User(
                username = i["username"],
                password_hash = hashed_password,
                role = i["role"],
                marked_for_deletion = i["marked_for_deletion"],
                total_loans = i["total_loans"],
                total_listings = i["total_listings"],
                join_date = i["join_date"],
            )

            db.session.add(user)
        db.session.commit()

        listings = [

            {
                "title": "The Shining ",
                "author": "Stephen King",
                "description": "A thrilling horror read",
                "genre_id": 4,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 3
                
            },
            {
                "title": "Alice in Wonderland ",
                "author": " Lewis Carroll",
                "description": "A lovely fairy story, with a rabbit!",
                "genre_id": 10,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 8
            },
            {
                "title": "Book3 ",
                "author": " author 2",
                "description": "an interesting read ",
                "genre_id": 5,
                "is_available": False,
                "marked_for_deletion": False,
                "user_id": 7
            },
            {
                "title": " Book5",
                "author": " Author 5",
                "description": "A sad story ",
                "genre_id": 3,
                "is_available": False,
                "marked_for_deletion": True,
                "user_id": 2
            },
            {
                "title": "Book6",
                "author": "Author 6 ",
                "description": "Very funny book ",
                "genre_id": 9,
                "is_available": False,
                "marked_for_deletion": False,
                "user_id": 10
            },
            {
                "title": " Book 7",
                "author": "Author 7 ",
                "description": " Scary story ",
                "genre_id": 4,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 8
            },
            {
                "title": "Book8 ",
                "author": " author 8",
                "description": " Happy romantic story",
                "genre_id": 3,
                "is_available": False,
                "marked_for_deletion": False,
                "user_id": 9
            },
            {
                "title": " Book10",
                "author": " author10",
                "description": "Lots of interesting things ",
                "genre_id": 2,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 5
            },
            {
                "title": " Book4",
                "author": "author 4 ",
                "description": " An interesting read",
                "genre_id": 8,
                "is_available": False,
                "marked_for_deletion": False,
                "user_id": 2
            },
            {
                "title": " Book14",
                "author": "author14 ",
                "description": " Keeps you gripped",
                "genre_id": 5,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 1
            }
        ]

        for l in listings:
            listing = Listing(
                title = l["title"],
                author = l["author"],
                description = l["description"],
                genre_id = l["genre_id"],
                is_available = l["is_available"],
                marked_for_deletion = l["marked_for_deletion"],
                user_id = l["user_id"],
            )
            db.session.add(listing)
        db.session.commit()

        loans = [
            {
                "listing_id": 5,
                "user_id": 7,
                "start_date": date(2025, 5, 14),
                "return_date": date(2025, 6, 11),
                "actual_return_date": None,
                "is_returned": False
            },
            {
                "listing_id": 4,
                "user_id": 10,
                "start_date": date(2024, 12, 10),
                "return_date": date(2025, 1, 7),
                "actual_return_date": date(2025, 1, 7),
                "is_returned": True
            },
            {
                "listing_id": 3,
                "user_id": 6,
                "start_date": date(2025, 6, 1),
                "return_date": date(2025, 6, 29),
                "actual_return_date": None,
                "is_returned": False
            },
            {
                "listing_id": 10,
                "user_id": 5,
                "start_date": date(2024, 12, 1),
                "return_date": date(2024, 12, 28),
                "actual_return_date": date(2024, 12, 27),
                "is_returned": True
            },
            {
                "listing_id": 6,
                "user_id": 2,
                "start_date": date(2025, 1, 1),
                "return_date": date(2025, 1, 29),
                "actual_return_date": date(2025, 1, 28),
                "is_returned": True
            },
            {
                "listing_id": 9 ,
                "user_id": 3,
                "start_date": date(2025, 5, 30),
                "return_date": date(2025, 6, 27),
                "actual_return_date": None,
                "is_returned": False
            },
            {
                "listing_id": 8,
                "user_id": 5,
                "start_date": date(2025, 3, 14),
                "return_date": date(2025, 4, 11),
                "actual_return_date": date(2025, 4, 11),
                "is_returned": True
            },
            {
                "listing_id": 2,
                "user_id": 1,
                "start_date": date(2025, 2, 1),
                "return_date": date(2025, 2, 28),
                "actual_return_date": date(2025, 2, 28),
                "is_returned": True
            },
            {
                "listing_id": 7 ,
                "user_id": 10,
                "start_date": date(2025, 5, 10),
                "return_date": date(2025, 6, 7),
                "actual_return_date": None,
                "is_returned": False
            },
            {
                "listing_id": 8,
                "user_id": 9,
                "start_date": date(2025, 4, 1),
                "return_date": date(2025, 4, 28),
                "actual_return_date": date(2025, 4, 28),
                "is_returned": True
            }
        ]

        for i in loans:
            loan = Loan(
                listing_id = i["listing_id"],
                user_id = i["user_id"],
                start_date = i["start_date"],
                return_date = i["return_date"],
                actual_return_date = i["actual_return_date"],
                is_returned = i["is_returned"]
            )
            db.session.add(loan)
        db.session.commit()