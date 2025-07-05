from app import create_app
from app.seed import seeding
from flask import redirect, url_for


app = create_app()

seeding()

if __name__ == '__main__':

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    app.run(debug=True)
