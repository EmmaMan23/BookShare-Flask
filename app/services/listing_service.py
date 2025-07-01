from app.models import Listing, Loan, Genre, User
from app.utils import Result
from app.extensions import db
from datetime import date, timedelta, datetime
from flask import url_for
from app.services.validators import validate_non_empty_string
from sqlalchemy.orm import joinedload
from app.services.dashboard_service import DashboardService
from flask_login import current_user
from sqlalchemy import and_

class ListingService:
    def __init__(self, db_session, dashboard_service):
        self.db_session = db_session
        self.dashboard_service = dashboard_service


    def list_book(self, title, author, description, genre_id, user_id, is_available=True):
        try:
            title = validate_non_empty_string(title, "Title")
            date_listed = date.today()

            new_listing = Listing(
                title=title,
                author=author,
                description=description,
                genre_id=genre_id,
                user_id=user_id,
                is_available=is_available,
                date_listed=date_listed,
                )
            
            user = self.db_session.query(User).get(user_id)
            if user.total_listings is None:
                user.total_listings = 1
            else:
                user.total_listings += 1
            self.db_session.add(new_listing)
            
            self.db_session.commit()
            self.dashboard_service.update_overall_listings()

            return Result(True, "Listing created successfully", new_listing)
        except Exception as e:
            return Result(False, f"Error creating Listing: {str(e)}")


    def get_all_listings(self, user_id = None, genre=None, availability=None, search=None, sort_order='desc'):
        query = self.db_session.query(Listing).options(
        joinedload(Listing.loans).joinedload(Loan.user))


        if user_id:
            query = query.filter(Listing.user_id == user_id)
        if genre:
            query = query.filter(Listing.genre.has(name=genre))
        if availability is not None:
            query = query.filter(Listing.is_available == availability)
        if search:
            search_query = f"%{search}%"
            query = query.filter(
                (Listing.title.ilike(search_query)) |
                (Listing.author.ilike(search_query))
            )
        if sort_order == 'asc':
            query = query.order_by(Listing.date_listed.asc())
        else:
            query = query.order_by(Listing.date_listed.desc())

        return query.all()

    def get_all_genres(self):
        return self.db_session.query(Genre).order_by(Genre.name).all()

    def get_listing_by_id(self, listing_id):
        return self.db_session.get(Listing, listing_id)

    def edit_listing(
        self,
        listing_id,
        user_id,
        title=None,
        author=None,
        description=None,
        genre_id=None,
        is_available=None,
        marked_for_deletion=None):

        listing = self.get_listing_by_id(listing_id)
        if not listing:
            return Result(False, "Listing not found")

        if not (current_user.is_admin or listing.user_id == user_id):
            return Result(False, "You can't edit someone else's listing")

        try:
            if title is not None:
                listing.title = validate_non_empty_string(title, "Title")
            if author is not None:
                listing.author = author.strip()
            if description is not None:
                listing.description = description.strip()
            if genre_id not in [None, '']:
                listing.genre_id = int(genre_id)
            else:
                listing.genre_id = None

            if is_available is not None:
                new_availability = is_available in ['true', 'on', '1', True]

                if listing.active_loan:
                    if new_availability != listing.is_available:
                        return Result(False, "Cannot change availability while listing is on loan")
                    

                if listing.marked_for_deletion:
                    return Result(False, "Cannot change availability while listing is marked for deletion")

                listing.is_available = new_availability

            if marked_for_deletion is not None:
                listing.marked_for_deletion = marked_for_deletion in ['true', 'on', '1', True]

            self.db_session.commit()
            return Result(True, "Listing updated successfully")

        except ValueError as ve:
            return Result(False, str(ve))

        except Exception as e:
            return Result(False, "An unexpected error occurred while updating listing")

    def update_marked_for_deletion(self, listing_id, is_marked):
        listing = self.db_session.get(Listing, listing_id)
        if not listing:
            return Result(False, "Listing not found.")
        
        try:
            listing.marked_for_deletion = is_marked
            listing.is_available = False
            self.db_session.commit()
            
            status_message = "marked for deletion" if is_marked else "unmarked for deletion"
            return Result(True, f"Listing successfully {status_message}.")
        except Exception as e:
            self.db_session.rollback() 
            return Result(False, f"Error updating deletion status: {str(e)}")

    def get_all_loans(self, status=None, sort_order='desc', search=None):
        query = self.db_session.query(Loan).join(Loan.user).join(Loan.listing)

        if status == 'active':
            query = query.filter(and_(Loan.actual_return_date == None, Loan.return_date > datetime.now()))
        elif status == 'past':
            query = query.filter(Loan.actual_return_date != None)
        elif status == 'overdue':
            query = query.filter(and_(Loan.actual_return_date == None, Loan.return_date < datetime.now()))

        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                (Listing.title.ilike(search_term)) |
                (User.username.ilike(search_term)))

        if sort_order == 'asc':
            query = query.order_by(Loan.start_date.asc())
        else:
            query = query.order_by(Loan.start_date.desc())
        print('status')

        return query.all()

    def get_loans_current_user(self, user_id, status=None, search=None, sort_order='desc'):
        query = self.db_session.query(Loan).filter_by(user_id=user_id).join(Loan.listing).join(Loan.user)

        if status == 'active':
            query = query.filter(and_(Loan.actual_return_date == None, Loan.return_date > datetime.now()))
        elif status == 'past':
            query = query.filter(Loan.actual_return_date != None)
        elif status == 'overdue':
            query = query.filter(and_(Loan.actual_return_date == None, Loan.return_date < datetime.now()))

        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                (Listing.title.ilike(search_term)) |
                (User.username.ilike(search_term))
            )

        if sort_order == 'asc':
            query = query.order_by(Loan.start_date.asc())
        else:
            query = query.order_by(Loan.start_date.desc())

        return query.all()


    def get_loan_by_id(self, loan_id):
        return self.db_session.get(Loan, loan_id)

    def update_loan(self, loan_id, actual_return_date):
        loan = self.db_session.get(Loan, loan_id)
        if not loan:
            return Result(False, "Loan not found"), None

        try:
            loan.is_returned = True
            loan.actual_return_date = actual_return_date

            listing = self.db_session.get(Listing, loan.listing_id)
            if listing:
                listing.is_available = True

            self.db_session.commit()
            return Result(True, "Loan marked as returned"), loan
        except Exception as e:
            return Result(False, f"Error updating loan: {str(e)}"), None


    def reserve_book(self, user_id, listing_id):
        
        try:
            start_date = date.today() + timedelta(days=1)
            return_date = start_date + timedelta(days=21)

            loan = Loan(
                user_id=user_id,
                listing_id=listing_id,
                start_date=start_date,
                return_date=return_date,
                is_returned= False
            )
            
            self.db_session.add(loan)

            listing = self.db_session.get(Listing, listing_id)
            if listing:
                listing.is_available = False
            
            user = self.db_session.query(User).get(user_id)
            if user.total_loans is None:
                user.total_loans = 1
            else:
                user.total_loans += 1

            self.db_session.commit()
            self.dashboard_service.update_overall_loans()
            return Result(True, "Book reserved successfully", loan)
        except Exception as e:
            return Result(False, f"Error reserving book: {str(e)}")
            