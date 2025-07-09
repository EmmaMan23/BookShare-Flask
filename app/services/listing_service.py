from app.models import Listing, Loan, Genre, User
from app.utils import Result
from datetime import date, timedelta
from app.services.validators import validate_non_empty_string, to_bool, validate_length
from flask_login import current_user


class ListingService:
    def __init__(self, db_session, dashboard_service):
        self.db_session = db_session
        self.dashboard_service = dashboard_service

    def list_book(self, title, author, description, genre_id, user_id, is_available=True):
        try:
            title = validate_non_empty_string(title, "Title")
            error = validate_length(title, "Title", 150)
            if error:
                return Result(False, error)

            error = validate_length(author, "Author", 50)
            if error:
                return Result(False, error)

            error = validate_length(description, "Description", 400)
            if error:
                return Result(False, error)
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

            user_result = self.get_record_by_id(User, user_id)
            if not user_result.success:
                return user_result
            user = user_result.data


            user.increment_totals(self.db_session)
            new_listing.save(self.db_session)
            self.dashboard_service.update_overall_listings()

            return Result(True, "Listing created successfully", new_listing)
        except Exception as e:
            return Result(False, f"Error creating Listing: {str(e)}")

    def get_all_listings(self, user_id=None, genre=None, availability=None, search=None, sort_order='desc', marked_for_deletion=None):
        query = Listing.filter_search_listings(
            db_session=self.db_session,
            user_id=user_id,
            search=search,
            filter_genre=genre,
            filter_availability=availability,
            sort_order=sort_order,
            marked_for_deletion=marked_for_deletion
        )

        return Result(True, "Listings returned successfully.", query)

    def get_all_genres(self):
        genres = Genre.get_all(self.db_session)
        return Result(True, "Genres retrieved successfully", genres)


    def get_record_by_id(self, model_cls, record_id, not_found_msg=None):
        record = model_cls.get_by_id(self.db_session, record_id)
        if record:
            return Result(True, f"{model_cls.__name__} found.", record)
        return Result(False, not_found_msg or f"{model_cls.__name__} not found.", None)


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

        result = self.get_record_by_id(Listing, listing_id)

        if not result.success:
            return Result(False, "Listing not found")

        listing = result.data

        if not (current_user.is_admin or listing.user_id == user_id):
            return Result(False, "You can't edit someone else's listing")

        try:
            if title is not None:
                title = validate_non_empty_string(title, "Title")
                error = validate_length(title, "Title", 150)
                if error:
                    return Result(False, error)
                listing.title = title

            if author is not None:
                author = author.strip()
                error = validate_length(author, "Author", 50)
                if error:
                    return Result(False, error)
                listing.author = author

            if description is not None:
                description = description.strip()
                error = validate_length(description, "Description", 400)
                if error:
                    return Result(False, error)
                listing.description = description

            if genre_id not in [None, '']:
                listing.genre_id = int(genre_id)
            else:
                listing.genre_id = None

            if is_available is not None:
                new_availability = to_bool(is_available)

                if listing.active_loan:
                    if new_availability != listing.is_available:
                        return Result(False, "Cannot change availability while listing is on loan")

                if listing.marked_for_deletion:
                    return Result(False, "Cannot change availability while listing is marked for deletion")

                listing.is_available = new_availability

            listing.save(self.db_session)
            return Result(True, "Listing updated successfully")

        except ValueError as ve:
            return Result(False, str(ve))

        except Exception as e:
            return Result(False, "An unexpected error occurred while updating listing")


    def update_marked_for_deletion(self, listing_id, is_marked):
        result = self.get_record_by_id(Listing, listing_id)
        if not result.success:
            return result

        listing = result.data

        try:
            listing.marked_for_deletion = to_bool(is_marked)
            listing.save(self.db_session)
            return Result(True, "Listing deletion status updated.")
        except Exception as e:
            return Result(False, f"Error updating deletion status: {str(e)}")

    def get_all_loans(self, user_id=None, status=None, sort_order='desc', search=None):
        loans = Loan.filter_search_loans(
            db_session=self.db_session,
            filter_status=status,
            search=search,
            sort_order=sort_order,
            user_id=user_id
        )

        return Result(True, "Loans retrieved successfully", loans)


    def update_loan(self, loan_id, actual_return_date):
        loan_result = self.get_record_by_id(Loan, loan_id)
        if not loan_result.success:
            return loan_result, None

        loan = loan_result.data

        try:
            loan.is_returned = True
            loan.actual_return_date = actual_return_date

            listing = loan.listing
            if listing:
                listing.is_available = True
                listing.save(self.db_session)

            loan.save(self.db_session)
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
                is_returned=False
            )

            listing_result = self.get_record_by_id(Listing, listing_id)
            if not listing_result.success:
                return Result(False, "Listing not found")

            listing = listing_result.data

            if not listing.is_available:
                return Result(False, "Listing not available for reservation")

            listing.is_available = False
            listing.save(self.db_session)

            user_result = self.get_record_by_id(User, user_id)
            if not user_result.success:
                return user_result  
            user = user_result.data


            user.total_loans = (user.total_loans or 0) + 1
            user.save(self.db_session)

            loan.save(self.db_session)
            self.dashboard_service.update_overall_loans()

            return Result(True, "Book reserved successfully", loan)
        except Exception as e:
            return Result(False, f"Error reserving book: {str(e)}")
