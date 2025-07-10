from app import create_app
from app.seed import seeding
from flask import redirect, url_for, request, abort
from app.extensions import db

# Create the Flask app instance
app = create_app()

# Populate the database with initial data (if needed)
with app.app_context():
    seeding()

@app.route('/reset-db')
def reset_db():
    if request.args.get('key') != 'reset123':  
        abort(403)
    with app.app_context():
        db.drop_all()
        db.create_all()
        seeding()
    return "Database reset and seeded!"

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # Run the Flask development server with debugging enabled
    app.run(debug=True)
