from app import db
from app.services.dashboard_service import DashboardService
from app.services.listing_service import ListingService

dashboard_service = DashboardService(db.session, "app/static/metrics.json")
listing_service = ListingService(db.session, dashboard_service)
