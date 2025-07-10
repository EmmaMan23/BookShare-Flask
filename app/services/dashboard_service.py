from app.utils import Result
import json
from app.models import Listing, Loan


class DashboardService:

    def __init__(self, db_session, metrics_file_path):
        """ Initialises the DashboardService with a database session and a path to the metrics JSON file """
        self.db_session = db_session
        self.metrics_file = metrics_file_path

    def read_metrics(self, user=None):
        """ Reads metrics from the JSON file. If a user is provided, their personal statistics
        and system-wide counts are also added to the result """

        try:
            # Load existing metrics from the JSON file
            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            if user:
                # Add user's listing/loan totals (from model properties or fallback to 0)
                data["user_total_listings"] = getattr(user, "total_listings", 0) or 0
                data["user_total_loans"] = getattr(user, "total_loans", 0) or 0

                # Query live counts for user's active listings and loans
                data["user_active_listings"] = Listing.count_by_user(
                    self.db_session, user.user_id)
                data["user_active_loans"] = Loan.count_active_by_user(
                    self.db_session, user.user_id)

                # Add system-wide counts for live dashboard display
                data["active_loans"] = Loan.count_active(self.db_session)
                data["listed_books"] = Listing.count_all(self.db_session)
                data["available_books"] = Listing.count_available(self.db_session)

            return Result(True, "Metrics read successfully", data)

        except Exception as e:
            # Catch any file read or JSON parsing errors
            return Result(False, f"Error reading metrics: {e}")

    def update_overall_listings(self):
        """ Increments the total number of listings in the metrics JSON file.
        Used when a new book is listed """

        try:
            # Read current metrics from the file
            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            # Increment the listing counter (initializes to 0 if missing)
            data['total_overall_books'] = data.get('total_overall_books', 0) + 1

            # Write updated metrics back to the file
            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=4)

            return Result(True, "Overall listings updated")

        except Exception as e:
            return Result(False, f"Error updating metrics JSON: {e}")
        
    def update_overall_loans(self):
        """
        Increments the total number of loans in the metrics JSON file.
        Used when a loan is successfully created.
        """
        try:
            # Read current metrics from the file
            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            # Increment the loan counter (initializes to 0 if missing)
            data['total_overall_loans'] = data.get('total_overall_loans', 0) + 1

            # Write updated metrics back to the file
            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=4)

            return Result(True, "Overall loans updated")

        except Exception as e:
            return Result(False, f"Error updating metrics JSON: {e}")
