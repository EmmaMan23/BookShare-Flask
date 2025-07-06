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
                "image": "images/science.png"
            },
            {
                "name": "Fantasy",
                "image": "images/fantasy.png"
            },
            {
                "name": "Romance",
                "image": "images/romance.png"
            },
            {
                "name": "Horror",
                "image": "images/horror.png"
            },
            {
                "name": "Mystery",
                "image": "images/mystery.png"
            },
            {
                "name": "Thriller",
                "image": "images/horror.png"
            },
            {
                "name": "History",
                "image": "images/adventure.png"
            },
            {
                "name": "Non-Fiction",
                "image": "images/science.png"
            },
            {
                "name": "Adventure",
                "image": "images/adventure.png"
            },
            {
                "name": "Children",
                "image": "images/children.png"
            }
        ]

        for g in genres:
            genre = Genre(
                name=g["name"],
                image=g["image"]
            )
            db.session.add(genre)
        db.session.commit()

        users = [
            {
                "username": "clive",
                "password": "Shoes123",
                "role": "admin",
                "marked_for_deletion": False,
                "total_loans": 1,
                "total_listings": 1,
                "join_date": date(2024, 9, 10)

            },
            {
                "username": "sally",
                "password": "Shoes345",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 5,
                "total_listings": 7,
                "join_date": date(2025, 2, 10)
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
                "join_date": date(2025, 1, 14)
            },
            {
                "username": "sebastian",
                "password": "Dogs",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 9,
                "total_listings": 3,
                "join_date": date(2024, 11, 29)
            },
            {
                "username": "sam",
                "password": "Ducks",
                "role": "admin",
                "marked_for_deletion": False,
                "total_loans": 2,
                "total_listings": 4,
                "join_date": date(2025, 2, 27)
            },
            {
                "username": "sophie",
                "password": "Llamas45",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 5,
                "total_listings": 2,
                "join_date": date(2025, 3, 8)
            },
            {
                "username": "charlie",
                "password": "Piesforever",
                "role": "regular",
                "marked_for_deletion": True,
                "total_loans": 5,
                "total_listings": 1,
                "join_date": date(2024, 12, 1)
            },
            {
                "username": "chantelle",
                "password": "Gingerfluff",
                "role": "admin",
                "marked_for_deletion": False,
                "total_loans": 6,
                "total_listings": 8,
                "join_date": date(2025, 5, 19)
            },
            {
                "username": "nathan",
                "password": "Ilovefootball",
                "role": "regular",
                "marked_for_deletion": False,
                "total_loans": 5,
                "total_listings": 1,
                "join_date": date(2025, 4, 5)
            }
        ]

        for i in users:
            hashed_password = generate_password_hash(i["password"])
            user = User(
                username=i["username"],
                password_hash=hashed_password,
                role=i["role"],
                marked_for_deletion=i["marked_for_deletion"],
                total_loans=i["total_loans"],
                total_listings=i["total_listings"],
                join_date=i["join_date"],
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
                "user_id": 3,
                "date_listed": date(2025, 1, 11),

            },
            {
                "title": "Alice in Wonderland ",
                "author": " Lewis Carroll",
                "description": "A lovely fairy story, with a rabbit!",
                "genre_id": 10,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 8,
                "date_listed": date(2025, 2, 11),
            },
            {
                "title": "The Colour of Magic",
                "author": " Terry Pratchett",
                "description": "Fantastical tale full of magic and wizardry.",
                "genre_id": 2,
                "is_available": False,
                "marked_for_deletion": False,
                "user_id": 7,
                "date_listed": date(2024, 12, 11),
            },
            {
                "title": "A History of Britain",
                "author": "Bob Smith",
                "description": "Discover a History of Britain through the years.",
                "genre_id": 7,
                "is_available": False,
                "marked_for_deletion": True,
                "user_id": 2,
                "date_listed": date(2025, 1, 11),
            },
            {
                "title": "Space",
                "author": "Shelly Jones",
                "description": "Space spectacular, informative information. ",
                "genre_id": 8,
                "is_available": False,
                "marked_for_deletion": False,
                "user_id": 10,
                "date_listed": date(2025, 5, 2),
            },
            {
                "title": "True Crime",
                "author": "Charlotte Peter",
                "description": "A thrilling real life crime stories",
                "genre_id": 6,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 8,
                "date_listed": date(2024, 12, 30),
            },
            {
                "title": "Book of seasons ",
                "author": "Fred Baxter",
                "description": "A colourful look at seasons through the year.",
                "genre_id": 8,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 9,
                "date_listed": date(2025, 6, 4),
            },
            {
                "title": "A Tale of love",
                "author": "John Lovett",
                "description": "A happy romantic tale of love.",
                "genre_id": 3,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 5,
                "date_listed": date(2024, 11, 17),
            },
            {
                "title": "Secret Museum",
                "author": "Mel Anderson",
                "description": "What will you discover in the secret museum?",
                "genre_id": 9,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 2,
                "date_listed": date(2025, 7, 1),
            },
            {
                "title": "Minority Report",
                "author": "Philip K Dick",
                "description": "Futuristic and fantastic, will keep you gripped.",
                "genre_id": 1,
                "is_available": True,
                "marked_for_deletion": False,
                "user_id": 1,
                "date_listed": date(2024, 12, 20),
            }
        ]

        for l in listings:
            listing = Listing(
                title=l["title"],
                author=l["author"],
                description=l["description"],
                genre_id=l["genre_id"],
                is_available=l["is_available"],
                marked_for_deletion=l["marked_for_deletion"],
                user_id=l["user_id"],
                date_listed=l["date_listed"],
            )
            db.session.add(listing)
        db.session.commit()

        loans = [
            {
                "listing_id": 5,
                "user_id": 7,
                "start_date": date(2025, 6, 14),
                "return_date": date(2025, 7, 3),
                "actual_return_date": None,
                "is_returned": False
            },
            {
                "listing_id": 4,
                "user_id": 10,
                "start_date": date(2025, 4, 10),
                "return_date": date(2025, 5, 7),
                "actual_return_date": date(2025, 5, 7),
                "is_returned": True
            },
            {
                "listing_id": 3,
                "user_id": 6,
                "start_date": date(2025, 7, 1),
                "return_date": date(2025, 8, 1),
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
                "listing_id": 10,
                "user_id": 3,
                "start_date": date(2025, 5, 30),
                "return_date": date(2025, 6, 27),
                "actual_return_date": date(2025, 6, 27),
                "is_returned": True
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
                "listing_id": 7,
                "user_id": 10,
                "start_date": date(2025, 6, 10),
                "return_date": date(2025, 7, 2),
                "actual_return_date": date(2025, 7, 3),
                "is_returned": True
            },
            {
                "listing_id": 8,
                "user_id": 9,
                "start_date": date(2025, 6, 1),
                "return_date": date(2025, 7, 3),
                "actual_return_date": date(2025, 7, 2),
                "is_returned": True
            }
        ]

        for i in loans:
            loan = Loan(
                listing_id=i["listing_id"],
                user_id=i["user_id"],
                start_date=i["start_date"],
                return_date=i["return_date"],
                actual_return_date=i["actual_return_date"],
                is_returned=i["is_returned"]
            )
            db.session.add(loan)
        db.session.commit()
