from app.models import Listing, Loan, Genre, User
from app.utils import Result
from app.extensions import db
from datetime import date, timedelta
from flask import url_for
from app.services.validators import validate_non_empty_string
from sqlalchemy.orm import joinedload
from app.services.dashboard_service import DashboardService
from flask_login import current_user

class ListingService:
    def __init__(self, db_session, dashboard_service):
        self.db_session = db_session
        self.dashboard_service = dashboard_service


    def list_book(self, title, author, description, genre_id, user_id, is_available=True):
        try:

            new_listing = Listing(
                title=title,
                author=author,
                description=description,
                genre_id=genre_id,
                user_id=user_id,
                is_available=is_available,
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


    def get_all_listings(self, user_id = None, genre=None, availability=None, search=None):
        query = self.db_session.query(Listing).order_by(Listing.title).options(
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
            print("DEBUG: Listing not found")
            return Result(False, "Listing not found")

        if not (current_user.is_admin or listing.user_id == user_id):
            print("DEBUG: Permission denied")
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
                
                print(f"DEBUG: Current availability: {listing.is_available}, New availability: {new_availability}")
                if listing.active_loan:
                    if new_availability != listing.is_available:
                        print("DEBUG: Cannot change availability - on loan")
                        return Result(False, "Cannot change availability while listing is on loan")
                    else:

                        print("DEBUG: Availability unchanged - on loan")

                if listing.marked_for_deletion:
                    print("DEBUG: Cannot change availability - marked for deletion")
                    return Result(False, "Cannot change availability while listing is marked for deletion")

                listing.is_available = new_availability

            if marked_for_deletion is not None:
                listing.marked_for_deletion = marked_for_deletion in ['true', 'on', '1', True]

            self.db_session.commit()
            print("DEBUG: Commit successful")
            return Result(True, "Listing updated successfully")

        except Exception as e:
            print(f"DEBUG: Exception occurred: {e}")
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

    def get_all_loans(self):
        return self.db_session.query(Loan).order_by(Loan.return_date.desc()).all()

    def get_loans_current_user(self, user_id):
        return self.db_session.query(Loan).filter_by(user_id=user_id).order_by(Loan.return_date.desc()).all()


    def update_loan(self, user_id, loan_id, actual_return_date):
        loan = self.db_session.get(Loan, loan_id)
        if not loan:
            return Result(False, "Loan not found")

        try:
            loan.is_returned = True
            loan.actual_return_date = actual_return_date
            
            listing = self.db_session.get(Listing, loan.listing_id)
            if listing:
                listing.is_available = True

            self.db_session.commit()
            return Result(True, "Loan marked as returned")
        except Exception as e:
            return Result(False, f"Error updating loan: {str(e)}")



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
            