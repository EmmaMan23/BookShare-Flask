from app import create_app
from app.seed import seeding
from flask import redirect, url_for

# Create the Flask app instance
app = create_app()

# Populate the database with initial data (if needed)
with app.app_context():
    seeding()

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # Run the Flask development server with debugging enabled
    app.run(debug=True)
