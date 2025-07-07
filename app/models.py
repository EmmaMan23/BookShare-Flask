from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import logging
from datetime import datetime, date
from sqlalchemy import and_, func


class baseModel(db.Model):
    __abstract__ = True

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            logging.error(f"Failed to save {self}: {e}")
            return False

    def delete(self, db_session):
        try:
            db_session.delete(self)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            logging.error(f"Failed to delete {self}: {e}")
            return False

    @classmethod
    def get_by_id(cls, db_session, record_id):
        try:
            record = db_session.get(cls, record_id)
            return record
        except Exception as e:
            logging.error(
                f"Failed to get record {cls.__name__} with id={record_id}: {e}")
            return None

    @classmethod
    def get_all(cls, db_session):
        try:
            records = db_session.query(cls).all()
            return records
        except Exception as e:
            logging.error(f"Failed to get records {cls.__name__}: {e}")
            return None


class User(baseModel, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    marked_for_deletion = db.Column(db.Boolean, default=False)
    total_loans = db.Column(db.Integer)
    total_listings = db.Column(db.Integer)
    join_date = db.Column(db.Date, default=date.today())
    listings = db.relationship(
        'Listing', back_populates='user', cascade='all, delete-orphan', passive_deletes=True)
    loans = db.relationship('Loan', back_populates='user',
                            cascade='all, delete-orphan', passive_deletes=True)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)

    @classmethod
    def existing_user(cls, db_session, username):
        return db_session.query(cls).filter(func.lower(cls.username) == username.lower()).first()

    @classmethod
    def count_admins(cls, db_session):
        return db_session.query(cls).filter_by(role='admin').count()

    @classmethod
    def filter_search_query(cls, db_session, search=None, filter_role=None, marked_for_deletion=None, sort_join_date='desc'):
        query = db_session.query(cls)

        if search:
            query = query.filter(cls.username.ilike(f'%{search}%'))

        if filter_role in ('admin', 'regular'):
            query = query.filter(cls.role == filter_role)

        if marked_for_deletion == 'true':
            query = query.filter(cls.marked_for_deletion.is_(True))

        if sort_join_date == 'asc':
            query = query.order_by(cls.join_date.asc())
        else:
            query = query.order_by(cls.join_date.desc())

        return query.all()

    def increment_totals(self, db_session):
        if self.total_listings is None:
            self.total_listings = 1
        else:
            self.total_listings += 1
        return self.save(db_session)


class Listing(baseModel):
    listing_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    description = db.Column(db.String(400))
    genre_id = db.Column(db.Integer, db.ForeignKey(
        'genre.genre_id'), nullable=True)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    marked_for_deletion = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id', ondelete='CASCADE'), nullable=False)
    date_listed = db.Column(db.Date)
    user = db.relationship('User', back_populates='listings')
    genre = db.relationship('Genre', backref='listings')
    loans = db.relationship('Loan', back_populates='listing',
                            cascade='all, delete-orphan', passive_deletes=True)

    @property
    def active_loan(self):
        return next((loan for loan in self.loans if not loan.is_returned), None)

    @classmethod
    def filter_search_listings(cls, db_session, user_id=None, search=None, filter_genre=None, filter_availability=None, sort_order='desc', marked_for_deletion=None):
        query = db_session.query(cls)

        if user_id:
            query = query.filter(cls.user_id == user_id)
        if search:
            query = query.filter(
                (cls.title.ilike(f'%{search}%')) |
                (cls.author.ilike(f'%{search}%'))
            )

        if filter_genre:
            query = query.filter(Listing.genre.has(name=filter_genre))

        if filter_availability is not None:
            query = query.filter(Listing.is_available == filter_availability)

        if marked_for_deletion is True:
            query = query.filter(cls.marked_for_deletion.is_(True))

        if sort_order == 'asc':
            query = query.order_by(cls.date_listed.asc())
        else:
            query = query.order_by(cls.date_listed.desc())

        return query.all()

    @classmethod
    def count_by_user(cls, db_session, user_id):
        return db_session.query(cls).filter(cls.user_id == user_id).count()

    @classmethod
    def count_all(cls, db_session):
        return db_session.query(cls).count()

    @classmethod
    def count_available(cls, db_session):
        return db_session.query(cls).filter(cls.is_available.is_(True)).count()


class Loan(baseModel):
    loan_id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey(
        'listing.listing_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date)
    return_date = db.Column(db.Date)
    actual_return_date = db.Column(db.Date, nullable=True)
    is_returned = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='loans')
    listing = db.relationship('Listing', back_populates='loans')

    @classmethod
    def filter_search_loans(cls, db_session, user_id=None, filter_status=None, search=None, sort_order='desc'):
        query = db_session.query(cls).join(cls.listing).join(cls.user)

        if user_id is not None:
            query = query.filter(cls.user_id == user_id)

        if search:
            query = query.filter(
                (Listing.title.ilike(f'%{search}%')) |
                (User.username.ilike(f'%{search}%')) |
                (Listing.author.ilike(f'%{search}%'))
            )

        if filter_status:
            now = datetime.now()
            if filter_status == 'active':
                query = query.filter(and_(
                    cls.actual_return_date.is_(None),
                    cls.return_date > now
                ))
            elif filter_status == 'past':
                query = query.filter(cls.actual_return_date.isnot(None))

            elif filter_status == 'overdue':
                query = query.filter(and_(
                    cls.actual_return_date.is_(None),
                    cls.return_date < now
                ))

        if sort_order == 'asc':
            query = query.order_by(cls.start_date.asc())
        else:
            query = query.order_by(cls.start_date.desc())

        return query.all()

    @classmethod
    def count_active_by_user(cls, db_session, user_id):
        return db_session.query(cls).filter(cls.user_id == user_id, cls.is_returned.is_(False)).count()

    @classmethod
    def count_active(cls, db_session):
        return db_session.query(cls).filter(cls.is_returned.is_(False)).count()


class Genre(baseModel):
    genre_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    image = db.Column(db.String(255), nullable=True)

    @classmethod
    def exists_by_name(cls, db_session, name):
        return db_session.query(cls).filter(func.lower(cls.name) == name.lower()).first()
