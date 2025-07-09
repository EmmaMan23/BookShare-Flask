# BookShare Flask Web Application 

## Project overview 

BookShare is a community-focused web application that allows users to share and borrow books.
All users can browse and create book listings, reserve books, and manage their own listings and profile.
Admin users have additional privileges to manage all loans, listings, genres, and users.

## Features

### For All Users:
- Register and log in  
- List a book  
- Edit their own listings  
- Browse available books  
- Reserve books  
- View their own loan history  
- Edit user details  
- Request account deletion


### Admin-Only Features:
- Manage users (update roles, delete accounts)
- Delete any book listings
- Manage all loans (return books, delete records)
- Manage genres (create, edit, delete)



## Technologies Used
- Python 3  
- Flask (core framework)  
- SQLite (database)  
- SQLAlchemy (ORM)  
- Flask-Login (authentication)  
- Jinja2 (templating)  
- Bootstrap (styling)  
- JavaScript (for interactivity)  
- Pytest (testing)  



## Installation Instructions

### 1.Clone the Repository
In your terminal, use the commands to clone the repository & navigate into the project folder

```
git clone https://github.com/EmmaMan23/BookShare-Flask
cd BookShare-Flask
```

### 2.Create a Virtual Environment
Create and activate a virtual environment 
#### For Mac/Linux
```
python3 -m venv venv
source venv/bin/activate
```
#### For Windows
```
python -m venv venv
venv\Scripts\activate
```
### 3.Install Dependencies
```
pip install -r requirements.txt
```

### Set Environment Variables
This application uses environment variables to manage sensitive information and configuration settings. 
These variables are stored in a file named .env, which has not been committed for security reasons.
To configure the application you will need to create your own .env file.

To set up your .env file:
1.Copy the example environment file in the repository using the following command:
```
cp .env.example .env

```
2. The contents of the example file look like this 
```
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///app.db
ADMIN_CODE=your_admin_code
```

3. Open the `.env` file in a text editor and update the following variables:

`SECRET_KEY` Used for securely signing session data
`DATABASE_URL` Path to the SQLite database (leave as is unless using a different database)
`ADMIN_CODE` The special code used for validating admins during registration

4. Save the `.env` file. The application will automatically load these settings when it runs


>[!IMPORTANT]
>Before running the app: Ensure you replace your_secret_key and your_admin_code with your own secure values.
>These values are not provided in the repository for security reasons.
>Do not share or commit your .env file to any public repository. 



### Database Setup
This application uses an SQLite database, which is lightweight and does not require a separate database server.

The database file will be created automatically when you run the application for the first time (if it doesn’t already exist). The schema will also be created automatically. The default database file path is specified in your .env file under the `DATABASE_URL` variable (e.g., sqlite:///app.db).


### Running the application

After activating your virtual environment and installing dependencies, start the app:
```
python3 main.py
```
This will launch the Flask development server locally at http://127.0.0.1:5000/ by default
You can open this URL in your browser to use the application. 
To stop the server, press `Ctrl + C` in the terminal (works on both Mac and Windows).


### Testing Instructions
This project uses `pytest` for both unit tests and integration tests.
Make sure you are in the project root directory before running the tests. 

Run Tests (Mac/Linux):
`PYTHONPATH=. pytest`

Run Tests (Windows CMD):
```
set PYTHONPATH=.
pytest
```
Run Tests (Windows PowerShell):
```
$env:PYTHONPATH="."
pytest
```

### Deployment
Deployment for this application is not yet complete. The project is intended to be deployed using Render, a cloud platform that supports Flask applications.

