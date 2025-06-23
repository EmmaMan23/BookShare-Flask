from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Store hashed passwords 
    role = db.Column(db.String(50), nullable=False)       # e.g., 'admin', 'user'
    marked_for_deletion = db.Column(db.Boolean, default=False) #user can mark fo deletion
    listings = db.relationship('Listing', back_populates='user', cascade='all, delete-orphan', passive_deletes=True)
    loans = db.relationship('Loan', back_populates='user', cascade='all, delete-orphan', passive_deletes=True)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)

class Listing(db.Model):
    listing_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    description = db.Column(db.String (400))
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.genre_id'), nullable=True)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    marked_for_deletion = db.Column(db.Boolean, default=False) #user can mark fo deletion
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', back_populates='listings')
    genre = db.relationship('Genre', backref='listings')
    loans = db.relationship('Loan', back_populates='listing', cascade='all, delete-orphan', passive_deletes=True)
    
    @property
    def active_loan(self):
        return next((loan for loan in self.loans if not loan.is_returned), None)

class Loan(db.Model):
    loan_id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.listing_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    is_returned = db.Column(db.Boolean, default=True)
    user = db.relationship('User', back_populates='loans')
    listing = db.relationship('Listing', back_populates='loans')


class Genre(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    inactive = db.Column(db.Boolean, default=False) 