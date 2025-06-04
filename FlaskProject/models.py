from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Store hashed passwords 
    role = db.Column(db.String(50), nullable=False)       # e.g., 'admin', 'user'
    marked_for_deletion = db.Column(db.Boolean, default=False) #user can mark fo deletion

    @property
    def is_admin(self):
        return self.role == 'admin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)


    def __repr__(self):
        return f'<Users {self.username} ({self.role})>'
    
class Listing(db.Model):
    listing_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    description = db.Column(db.String (400))
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.genre_id'))
    is_available = db.Column(db.Boolean, default=True)
    marked_for_deletion = db.Column(db.Boolean, default=False) #user can mark fo deletion
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', backref='listings')
    genre = db.relationship('Genre', backref='listings')
    

    def __repr__(self):
        username = self.user.username if self.user else "No user"
        return f"<Listing {self.title} by User {username} (Available: {self.is_available})>"
    
class Loan(db.Model):
    loan_id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.listing_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    start_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    is_returned = db.Column(db.Boolean, default=True)
    user = db.relationship('User', backref='loans')
    listing = db.relationship('Listing', backref='loans')


class Genre(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    inactive = db.Column(db.Boolean, default=False) 