# Productivity Tool API

A secure Flask REST API for managing personal notes. Users can create accounts, log in using JWT authentication, and perform CRUD operations on their own notes.

## Features

- User registration and login
- JWT authentication
- Password hashing with Flask-Bcrypt
- Input validation with Marshmallow
- User-owned notes
- Create, read, update, and delete notes
- User isolation
- Pagination for notes
- Database migrations with Flask-Migrate
- Seed data for development
- Automated tests with pytest

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Bcrypt
- Flask-JWT-Extended
- Marshmallow
- SQLite
- pytest
- Pipenv

## Project Structure

productivity-api/
├── migrations/
├── server/
│   ├── __init__.py
│   ├── app.py
│   ├── auth.py
│   ├── models.py
│   ├── resources.py
│   ├── schemas.py
│   └── seed.py
├── tests/
│   ├── test_auth.py
│   └── test_notes.py
├── .gitignore
├── Pipfile
├── Pipfile.lock
└── pytest.ini
Installation

Clone the repository and enter the project directory:

git clone https://github.com/OMONDICALMAX/productivity-api.git
cd productivity-api

Install the project dependencies:

pipenv install

Activate the Pipenv environment:

pipenv shell
Environment Variables

Create a .env file in the project root:

JWT_SECRET_KEY=your-secret-key

The .env file should never be committed to Git.

Database Setup

Apply the database migrations:

pipenv run flask --app server.app db upgrade

Seed the database with sample data:

pipenv run python -m server.seed
Running the Application

Start the Flask development server:

pipenv run flask --app server.app run

The API will be available at:

http://127.0.0.1:5000
Authentication Endpoints
Sign Up
POST /signup

Request body:

{
  "username": "john",
  "email": "john@example.com",
  "password": "secret123"
}
Login
POST /login

Request body:

{
  "username": "john",
  "password": "secret123"
}

The response contains an access token.

Use the token in protected requests:

Authorization: Bearer <access_token>
Current User
GET /me

Requires authentication.

Notes Endpoints

All note endpoints require JWT authentication.

Create a Note
POST /notes

Request body:

{
  "title": "My first note",
  "content": "This is my note."
}
Get Notes
GET /notes

Supports pagination:

GET /notes?page=1&per_page=5

The response includes:

notes
current page
number of items per page
total notes
total pages
whether another page exists
whether a previous page exists
Get a Single Note
GET /notes/<note_id>
Update a Note
PATCH /notes/<note_id>

Request body can contain either or both fields:

{
  "title": "Updated title",
  "content": "Updated content."
}
Delete a Note
DELETE /notes/<note_id>

Returns:

204 No Content
User Isolation

Users can only access notes that belong to their authenticated account.

A user cannot:

view another user's notes
update another user's notes
delete another user's notes

Unauthorized access attempts return:

404 Not Found
Testing

Run the complete test suite:

pipenv run pytest -q

The current test suite contains 20 passing tests covering authentication, validation, CRUD operations, pagination, authentication requirements, and user isolation.

Database Migrations

Create a new migration after changing models:

pipenv run flask --app server.app db migrate -m "describe your changes"

Apply migrations:

pipenv run flask --app server.app db upgrade

Check the current migration:

pipenv run flask --app server.app db current
Seed Data

The seed script creates:

one sample user
seven sample notes

Seed data can be loaded with:

pipenv run python -m server.seed

The seed script checks for existing seed data before creating it, preventing duplicate seed records.

API Response Codes
Status Code	Meaning
200	Successful request
201	Resource created
204	Resource deleted successfully
400	Invalid request or validation error
401	Authentication required or invalid credentials
404	Resource not found
409	Username or email already exists
Security
Passwords are stored as bcrypt hashes rather than plain text.
Protected endpoints require JWT authentication.
Users can only access their own notes.
JWT secrets are stored in environment variables.
.env is excluded from version control.
License

This project was created as part of a Moringa School Software Engineering course project.