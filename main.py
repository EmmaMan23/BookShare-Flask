from app import create_app
from app.routes import auth
from app.seed import seeding


app = create_app()

seeding()


@app.route('/')
def home():
    return('Hello World')

if __name__ == '__main__':


    app.run(debug=True)