# Complete Testing Guide for FastAPI

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

# Assuming the app from 02_ADVANCED_PRODUCTION_APP.py

# ===========================
# TEST DATABASE SETUP
# ===========================

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)

# ===========================
# FIXTURES
# ===========================

@pytest.fixture
def db():
    """Database fixture for tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    """Test client fixture."""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def auth_token(client):
    """Get authentication token."""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Get authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}

# ===========================
# AUTHENTICATION TESTS
# ===========================

class TestAuthentication:
    def test_login_success(self, client):
        """Test successful login."""
        response = client.post(
            "/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post(
            "/token",
            data={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user."""
        response = client.get("/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without token."""
        response = client.get("/users/me")
        assert response.status_code == 401

    def test_invalid_token(self, client):
        """Test invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401

# ===========================
# ITEMS CRUD TESTS
# ===========================

class TestItems:
    def test_create_item(self, client, auth_headers):
        """Test creating an item."""
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": 99.99
        }
        response = client.post("/items/", json=item_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["price"] == 99.99
        assert "id" in data
        assert "created_at" in data

    def test_create_item_invalid_price(self, client, auth_headers):
        """Test creating item with invalid price."""
        item_data = {
            "name": "Test Item",
            "description": "A test item",
            "price": -99.99  # Invalid
        }
        response = client.post("/items/", json=item_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_item_missing_required_field(self, client, auth_headers):
        """Test creating item without required field."""
        item_data = {
            "description": "A test item",
            "price": 99.99
        }
        response = client.post("/items/", json=item_data, headers=auth_headers)
        assert response.status_code == 422

    def test_read_items(self, client, auth_headers):
        """Test reading items."""
        # Create some items first
        for i in range(3):
            item_data = {
                "name": f"Item {i}",
                "price": float(i + 10)
            }
            client.post("/items/", json=item_data, headers=auth_headers)
        
        # Read items
        response = client.get("/items/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_read_items_with_pagination(self, client, auth_headers):
        """Test reading items with pagination."""
        response = client.get(
            "/items/?skip=0&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_read_item_by_id(self, client, auth_headers):
        """Test reading a specific item."""
        # Create an item
        item_data = {
            "name": "Test Item",
            "price": 99.99
        }
        create_response = client.post(
            "/items/",
            json=item_data,
            headers=auth_headers
        )
        item_id = create_response.json()["id"]
        
        # Read the item
        response = client.get(f"/items/{item_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Test Item"

    def test_read_item_not_found(self, client, auth_headers):
        """Test reading non-existent item."""
        response = client.get("/items/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_read_item_invalid_id(self, client, auth_headers):
        """Test reading item with invalid ID."""
        response = client.get("/items/-1", headers=auth_headers)
        assert response.status_code == 422

    def test_update_item(self, client, auth_headers):
        """Test updating an item."""
        # Create an item
        item_data = {
            "name": "Original Name",
            "price": 99.99
        }
        create_response = client.post(
            "/items/",
            json=item_data,
            headers=auth_headers
        )
        item_id = create_response.json()["id"]
        
        # Update the item
        updated_data = {
            "name": "Updated Name",
            "price": 199.99
        }
        response = client.put(
            f"/items/{item_id}",
            json=updated_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["price"] == 199.99

    def test_delete_item(self, client, auth_headers):
        """Test deleting an item."""
        # Create an item
        item_data = {
            "name": "Test Item",
            "price": 99.99
        }
        create_response = client.post(
            "/items/",
            json=item_data,
            headers=auth_headers
        )
        item_id = create_response.json()["id"]
        
        # Delete the item
        response = client.delete(f"/items/{item_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # Verify deletion
        response = client.get(f"/items/{item_id}", headers=auth_headers)
        assert response.status_code == 404

# ===========================
# FILE UPLOAD TESTS
# ===========================

class TestFileHandling:
    def test_upload_file(self, client, auth_headers):
        """Test file upload."""
        content = b"test file content"
        files = {"file": ("test.txt", content, "text/plain")}
        data = {"description": "A test file"}
        
        response = client.post(
            "/upload/",
            files=files,
            data=data,
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert result["filename"] == "test.txt"
        assert result["size"] == len(content)
        assert result["description"] == "A test file"

    def test_upload_multiple_files(self, client, auth_headers):
        """Test uploading multiple files."""
        files = [
            ("file", ("test1.txt", b"content1", "text/plain")),
            ("file", ("test2.txt", b"content2", "text/plain")),
        ]
        
        response = client.post(
            "/upload-multiple/",
            files=files,
            headers=auth_headers
        )
        assert response.status_code == 200
        result = response.json()
        assert len(result["files"]) == 2

# ===========================
# BACKGROUND TASK TESTS
# ===========================

class TestBackgroundTasks:
    def test_send_email_task(self, client, auth_headers):
        """Test background task."""
        response = client.post(
            "/send-email/",
            json={"email": "test@example.com"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "scheduled" in response.json()["message"]

# ===========================
# HEALTH CHECK TESTS
# ===========================

class TestHealth:
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

# ===========================
# PERFORMANCE TESTS
# ===========================

class TestPerformance:
    def test_concurrent_requests(self, client, auth_headers):
        """Test handling concurrent requests."""
        responses = []
        for i in range(10):
            response = client.get("/items/", headers=auth_headers)
            responses.append(response)
        
        assert all(r.status_code == 200 for r in responses)

    def test_large_payload(self, client, auth_headers):
        """Test handling large payload."""
        large_description = "x" * 1000
        item_data = {
            "name": "Large Item",
            "description": large_description,
            "price": 99.99
        }
        response = client.post(
            "/items/",
            json=item_data,
            headers=auth_headers
        )
        assert response.status_code == 201

# ===========================
# EDGE CASES
# ===========================

class TestEdgeCases:
    def test_float_precision(self, client, auth_headers):
        """Test float precision in pricing."""
        item_data = {
            "name": "Test Item",
            "price": 99.99
        }
        response = client.post("/items/", json=item_data, headers=auth_headers)
        data = response.json()
        assert data["price"] == 99.99

    def test_special_characters_in_name(self, client, auth_headers):
        """Test special characters in item name."""
        item_data = {
            "name": "Test Item with @#$%&*()",
            "price": 99.99
        }
        response = client.post("/items/", json=item_data, headers=auth_headers)
        assert response.status_code == 201

    def test_unicode_characters(self, client, auth_headers):
        """Test unicode characters."""
        item_data = {
            "name": "测试物品 🚀",
            "description": "خیلی سوپر",
            "price": 99.99
        }
        response = client.post("/items/", json=item_data, headers=auth_headers)
        assert response.status_code == 201

# ===========================
# WEBSOCKET TESTS
# ===========================

class TestWebSocket:
    def test_websocket_connection(self, client):
        """Test WebSocket connection."""
        with client.websocket_connect("/ws/1") as websocket:
            data = websocket.receive_text()
            assert data

    def test_websocket_send_receive(self, client):
        """Test WebSocket send and receive."""
        with client.websocket_connect("/ws/1") as websocket:
            websocket.send_text("Hello")
            data = websocket.receive_text()
            assert "Hello" in data

# ===========================
# RUNNING TESTS
# ===========================

# Run with: pytest test_fastapi.py -v
# Run with coverage: pytest test_fastapi.py --cov=. --cov-report=html
# Run specific test: pytest test_fastapi.py::TestItems::test_create_item -v
