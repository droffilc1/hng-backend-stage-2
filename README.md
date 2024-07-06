# User and Organisation Management API

## Overview

This is a Flask-based RESTful API for managing users and organisations. The application allows for user registration, login, and the creation and management of organisations. Each user can belong to multiple organisations, and each organisation can have multiple users.

## Features

- **User Registration**: Users can register with their details. Upon registration, a default organisation is created for the user.
- **User Login**: Users can log in and receive a JWT token for accessing protected endpoints.
- **Organisation Management**: Users can create new organisations, view their organisations, and add other users to their organisations.
- **Validation and Error Handling**: All endpoints include validation and return appropriate error messages for invalid requests.

## Endpoints

### Authentication

- **\[POST\] /auth/register**: Registers a new user and creates a default organisation.
  - **Request Body**:
    ```json
    {
      "firstName": "string",
      "lastName": "string",
      "email": "string",
      "password": "string",
      "phone": "string"
    }
    ```
  - **Successful Response**:
    ```json
    {
      "status": "success",
      "message": "Registration successful",
      "data": {
        "accessToken": "eyJh...",
        "user": {
          "userId": "string",
          "firstName": "string",
          "lastName": "string",
          "email": "string",
          "phone": "string"
        }
      }
    }
    ```
- **\[POST\] /auth/login**: Logs in a user and returns a JWT token.
  - **Request Body**:
    ```json
    { "email": "string", "password": "string" }
    ```
  - **Successful Response**:
    ```json
    {
      "status": "success",
      "message": "Login successful",
      "data": {
        "accessToken": "eyJh...",
        "user": {
          "userId": "string",
          "firstName": "string",
          "lastName": "string",
          "email": "string",
          "phone": "string"
        }
      }
    }
    ```

### Organisations

- **\[GET\] /api/organisations**: Gets all organisations the logged-in user belongs to or created.
  - **Successful Response**:
    ```json
    {
      "status": "success",
      "message": "Organisations retrieved successfully",
      "data": {
        "organisations": [
          { "orgId": "string", "name": "string", "description": "string" }
        ]
      }
    }
    ```
- **\[GET\] /api/organisations/**
  : Gets a single organisation by ID.

  - **Successful Response**:

    ```json
    {
      "status": "success",
      "message": "Organisation retrieved successfully",
      "data": { "orgId": "string", "name": "string", "description": "string" }
    }
    ```

- **\[POST\] /api/organisations**: Creates a new organisation.

  - **Request Body**:
    ```json
    { "name": "string", "description": "string" }
    ```
  - **Successful Response**:

    ```json
    {
      "status": "success",
      "message": "Organisation created successfully",
      "data": { "orgId": "string", "name": "string", "description": "string" }
    }
    ```

- **\[POST\] /api/organisations/**
  **/users**: Adds a user to an organisation.

  - **Request Body**:

    ```json
    { "userId": "string" }
    ```

  - **Successful Response**:

    ```json
    {
      "status": "success",
      "message": "User added to organisation successfully"
    }
    ```

## Directory Structure

```plaintext
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   └── config.py
├── migrations/
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   └── test_organisation.py
├── .env
├── config.py
├── manage.py
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/droffilc1/hng-backend-stage-2
   cd hng-backend-stage-2
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file with your database and secret key configurations:

   ```env
   FLASK_APP=manage.py FLASK_ENV=development SECRET_KEY=your_secret_key SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost/dbname
   ```

5. Run the database migrations:

   ```bash
   flask db upgrade
   ```

6. Start the Flask application:

```bash
flask run
```

### Running Tests

To run the tests, use the following command:

```bash
python -m unittest discover tests
```

## Acknowledgements

- Flask:(https://flask.palletsprojects.com/)
- Flask-JWT-Extended: [https://flask-jwt-extended.readthedocs.io/](https://flask-jwt-extended.readthedocs.io/)
- SQLAlchemy: [https://www.sqlalchemy.org/](https://www.sqlalchemy.org/)
