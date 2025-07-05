from app.utils import Result
import json
from app.models import Listing, Loan


class DashboardService:

    def __init__(self, db_session, metrics_file_path):
        self.db_session = db_session
        self.metrics_file = metrics_file_path

    def read_metrics(self, user=None):
        with open(self.metrics_file, "r") as f:
            data = json.load(f)

        if user:
            data["user_total_listings"] = user.total_listings or 0
            data["user_total_loans"] = user.total_loans or 0

            data["user_active_listings"] = Listing.count_by_user(
                self.db_session, user.user_id)
            data["user_active_loans"] = Loan.count_active_by_user(
                self.db_session, user.user_id)

            data["active_loans"] = Loan.count_active(self.db_session)
            data["listed_books"] = Listing.count_all(self.db_session)
            data["available_books"] = Listing.count_available(self.db_session)

        return data

    def update_overall_listings(self):
        try:
            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            data['total_overall_books'] = data.get(
                'total_overall_books', 0) + 1

            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            return Result(False, f"Error updating metrics JSON: {e}")

    def update_overall_loans(self):
        try:
            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            data['total_overall_loans'] = data.get(
                'total_overall_loans', 0) + 1

            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            return Result(False, f"Error updating metrics JSON: {e}")
