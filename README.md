# Productivity Tool API

A secure Flask REST API for managing personal notes. Users can create accounts, authenticate using JWT tokens, and perform CRUD operations on their own notes.

## Features

* User registration and login
* JWT-based authentication
* Password hashing with Flask-Bcrypt
* Input validation with Marshmallow
* User-owned notes
* Create, read, update, and delete notes
* User isolation
* Pagination for notes
* Database migrations with Flask-Migrate
* Seed data for development
* Automated testing with pytest

## Technologies

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* Flask-Bcrypt
* Flask-JWT-Extended
* Marshmallow
* SQLite
* pytest
* Pipenv

## Project Structure

```text
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
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/OMONDICALMAX/productivity-api.git
cd productivity-api
```

### 2. Install Dependencies

```bash
pipenv install
```

### 3. Activate the Pipenv Environment

```bash
pipenv shell
```

## Environment Variables

Create a `.env` file in the project root:

```env
JWT_SECRET_KEY=your-secret-key
```

> **Important:** Never commit your `.env` file to Git. Make sure `.env` is included in your `.gitignore`.

## Database Setup

### Apply Database Migrations

```bash
pipenv run flask --app server.app db upgrade
```

### Seed the Database

Load the sample data:

```bash
pipenv run python -m server.seed
```

The seed script creates:

* One sample user
* Seven sample notes

The script checks for existing seed data before creating new records, helping prevent duplicate seed records.

## Running the Application

Start the Flask development server:

```bash
pipenv run flask --app server.app run
```

The API will be available at:

```text
http://127.0.0.1:5000
```

## API Endpoints

### Authentication

#### Sign Up

**POST** `/signup`

Request body:

```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "secret123"
}
```

#### Login

**POST** `/login`

Request body:

```json
{
  "username": "john",
  "password": "secret123"
}
```

The response contains an access token.

For protected requests, include the token in the `Authorization` header:

```text
Authorization: Bearer <access_token>
```

### Current User

#### Get Current User

**GET** `/me`

Requires JWT authentication.

## Notes

All note endpoints require JWT authentication.

### Create a Note

**POST** `/notes`

Request body:

```json
{
  "title": "My first note",
  "content": "This is my note."
}
```

### Get Notes

**GET** `/notes`

The endpoint supports pagination.

Example:

```text
GET /notes?page=1&per_page=5
```

The response includes:

* Notes
* Current page
* Number of items per page
* Total number of notes
* Total number of pages
* Whether another page exists
* Whether a previous page exists

### Get a Single Note

**GET** `/notes/<note_id>`

Returns a single note belonging to the authenticated user.

### Update a Note

**PATCH** `/notes/<note_id>`

The request body can contain either or both fields:

```json
{
  "title": "Updated title",
  "content": "Updated content."
}
```

### Delete a Note

**DELETE** `/notes/<note_id>`

Successful deletion returns:

```text
204 No Content
```

## User Isolation

The API enforces ownership of notes.

Authenticated users can only access notes belonging to their own account.

A user cannot:

* View another user's notes
* Update another user's notes
* Delete another user's notes

Unauthorized attempts to access another user's note return:

```text
404 Not Found
```

This prevents users from accessing resources that do not belong to them.

## API Response Codes

| Status Code | Meaning                                        |
| ----------- | ---------------------------------------------- |
| `200`       | Successful request                             |
| `201`       | Resource created                               |
| `204`       | Resource deleted successfully                  |
| `400`       | Invalid request or validation error            |
| `401`       | Authentication required or invalid credentials |
| `404`       | Resource not found                             |
| `409`       | Username or email already exists               |

## Testing

Run the complete test suite with:

```bash
pipenv run pytest -q
```

The current test suite contains **20 passing tests** covering:

* User authentication
* Registration validation
* Login validation
* CRUD operations
* Pagination
* Authentication requirements
* User isolation

## Database Migrations

After making changes to the database models, create a new migration:

```bash
pipenv run flask --app server.app db migrate -m "describe your changes"
```

Apply the migration:

```bash
pipenv run flask --app server.app db upgrade
```

Check the current migration:

```bash
pipenv run flask --app server.app db current
```

## Seed Data

The seed script can be used to populate the development database with sample data.

Run:

```bash
pipenv run python -m server.seed
```

The seed script creates:

* One sample user
* Seven sample notes

It checks whether the seed data already exists before creating records, preventing duplicate seed records.

## Security

The API includes several security measures:

* Passwords are stored as bcrypt hashes rather than plain text.
* Protected endpoints require JWT authentication.
* Users can only access their own notes.
* JWT secrets are stored in environment variables.
* `.env` is excluded from version control.
* Input data is validated using Marshmallow.

## Deployment

The API is deployed using Render.

**Live API:**

https://productivity-api-trd7.onrender.com

## License

This project was created by **Calmax Omondi** for educational purposes.
