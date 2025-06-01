from app import create_app, db
from models import User, Loan, Listing, Genre


app = create_app()

with app.app_context():
    db.create_all()
    print("Tables created")

