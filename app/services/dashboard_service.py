from app.extensions import db
from app.utils import Result
import json
import os

class DashboardService:

    def __init__(self, db_session, metrics_file_path):
        self.db_session = db_session
        self.metrics_file = metrics_file_path

    def read_metrics(self, user):
    
        with open(self.metrics_file, "r") as f:
            data = json.load(f)

        data["user_total_listings"] = user.total_listings or 0
        data["user_total_loans"] = user.total_loans or 0
        print(data)
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