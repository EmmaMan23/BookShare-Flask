from app import create_app
from routes import auth


app = create_app()


@app.route('/')
def home():
    return('Hello World')

if __name__ == '__main__':


    app.run(debug=True)