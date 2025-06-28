from app.extensions import db
from app.utils import Result
import json
from app.models import Listing, Loan
from datetime import date, timedelta
import os

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

            data["user_active_listings"] = (
                self.db_session.query(Listing)
                .filter(Listing.user_id == user.user_id)
                .count()
                )

                
            today = date.today()
            data["user_active_loans"] = (
                self.db_session.query(Loan)
                .filter(
                    Loan.user_id == user.user_id,
                    Loan.start_date <= today + timedelta(days=1),
                    Loan.return_date >= today
                    )
                .count()
                )
            
            data["active_loans"] = (
                self.db_session.query(Loan)
                .count()
                )
            
            data["listed_books"] = (
                self.db_session.query(Listing)
                .count()
            )
            data["available_books"] = (
                self.db_session.query(Listing)
                .filter(
                    Listing.is_available == True
                    )
                .count()
            )
            print (data)
            return data
    
    def update_overall_listings(self):
        try:
            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            data['total_overall_books'] = data.get('total_overall_books', 0) +1 

            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            return Result(False, f"Error updating metrics JSON: {e}")
        
    def update_overall_loans(self):
        try:
            with open(self.metrics_file, "r") as f:
                data = json.load(f)

            data['total_overall_loans'] = data.get('total_overall_loans', 0) +1 

            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            return Result(False, f"Error updating metrics JSON: {e}")