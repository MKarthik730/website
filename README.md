This project provides a simple, production-style REST API using FastAPI, SQLAlchemy ORM, and PostgreSQL for CRUD (Create, Read, Update, Delete) operations on user data.

🚀 Features
Create 👤: Add new users (name, age, phone number, salary) to the database.

Read 📄:

List all users.

Search users by name.

Update ✏️: Edit an existing user's fields by name.

Delete 🗑️: Remove users using their database ID.

CORS: Out-of-the-box setup for browser-based testing and frontend integration.

Production-ready Database Layer: SQLAlchemy ORM models, tested with PostgreSQL.

Dependency Injection: Cleaner, safer DB session management.

Pydantic Integration: Robust data validation (recommended for all endpoints).

🛤️ API Endpoints
Method	Endpoint	Description
GET	/	Health check
GET	/users	Get all users
POST	/users	Add a new user
DELETE	/users/{id}	Delete user by ID
GET	/users/search	Search user by name (query)
PUT	/users	Update user fields by name


🏁 Quickstart
bash
# Clone the repo
git clone https://github.com/MKarthik730/website.git
cd website

# Install dependencies
pip install fastapi[all] sqlalchemy psycopg2-binary

# Configure your PostgreSQL database/URL (see .env.example)
# Run the app
uvicorn main:app --reload
Visit your API docs at http://127.0.0.1:8000/docs

📸 Demo
You can add screenshots/gifs showing your API in action, or how to use the provided HTML UI with you

