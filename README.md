# website
This project provides a simple, production-style REST API built with FastAPI, SQLAlchemy ORM, and PostgreSQL to perform CRUD (Create, Read, Update, Delete) operations on user data.  
Features
Create a User: Add new users (name, age, phone number, salary) to the database.

Read Users:

List all users.

Search for a user by name.

Update a User: Update an existing user’s fields by name.

Delete a User: Remove users by their database ID.

CORS: Configured for browser-based testing.

Database Layer: SQLAlchemy ORM models, PostgreSQL configured.

Dependency Injection: Clean DB session management.

Pydantic Integration: (Suggested for strict validation.)

Endpoints
Method	Endpoint	Description
GET	/	Health check
GET	/users	Get all users
POST	/users	Add a new user
DELETE	/users/{id}	Delete user by ID
GET	/users/search	Search user by name (query arg)
PUT	/users	Update user fields by name

