import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import Item, ItemStatus

# In-memory SQLite engine dedicated to test execution
TEST_DB_URL = "sqlite://"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ==========================================
# 1. POST /items (Create Item Tests)
# ==========================================

def test_create_item_success(client: TestClient):
    payload = {
        "title": "MacBook Air M2",
        "description": "Midnight blue 13-inch laptop left on table 4",
        "category": "Electronics",
        "location": "Central Library Hall A",
        "reported_by": "Sarah Connor",
        "status": "Lost"
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "MacBook Air M2"
    assert data["description"] == payload["description"]
    assert data["category"] == "Electronics"
    assert data["location"] == "Central Library Hall A"
    assert data["reported_by"] == "Sarah Connor"
    assert data["status"] == "Lost"


def test_create_item_validation_empty_title(client: TestClient):
    payload = {
        "title": "   ",
        "description": "Silver stainless steel water bottle",
        "category": "Accessories",
        "location": "Gymnasium",
        "reported_by": "John Doe",
        "status": "Found"
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 422


def test_create_item_validation_short_description(client: TestClient):
    payload = {
        "title": "Calculator",
        "description": "ab",  # Less than 3 characters
        "category": "Electronics",
        "location": "Math Lab Room 204",
        "reported_by": "Alice Smith",
        "status": "Lost"
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 422


def test_create_item_validation_invalid_status(client: TestClient):
    payload = {
        "title": "Student ID Card",
        "description": "Card belonging to Computer Science dept student",
        "category": "Documents",
        "location": "Cafeteria Counter 2",
        "reported_by": "Cafeteria Staff",
        "status": "Pending"  # Invalid status (only Lost, Found, Returned permitted)
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 422


def test_create_item_validation_missing_field(client: TestClient):
    payload = {
        "title": "Notebook",
        # Missing description
        "category": "Stationery",
        "location": "Room 101",
        "reported_by": "Bob",
        "status": "Lost"
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 422


# ==========================================
# 2. GET /items (List Items Tests)
# ==========================================

def test_get_all_items(client: TestClient):
    # Initially empty
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []

    # Insert items
    client.post("/items", json={
        "title": "Black Umbrella",
        "description": "Automatic foldable umbrella with wooden handle",
        "category": "Accessories",
        "location": "Auditorium Entrance",
        "reported_by": "Security Desk",
        "status": "Found"
    })
    client.post("/items", json={
        "title": "Wristwatch",
        "description": "Casio G-Shock black resin strap digital watch",
        "category": "Accessories",
        "location": "Sports Complex Court 1",
        "reported_by": "Mark Dave",
        "status": "Lost"
    })

    res = client.get("/items")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 2
    assert items[0]["title"] == "Black Umbrella"
    assert items[1]["title"] == "Wristwatch"


# ==========================================
# 3. GET /items/{item_id} (Get Item by ID Tests)
# ==========================================

def test_get_item_by_id_success(client: TestClient):
    res_create = client.post("/items", json={
        "title": "Lab Coat",
        "description": "White chemistry lab coat size M with monogram",
        "category": "Clothing",
        "location": "Chemistry Lab 3",
        "reported_by": "Dr. Watson",
        "status": "Found"
    })
    item_id = res_create.json()["id"]

    res_get = client.get(f"/items/{item_id}")
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["id"] == item_id
    assert data["title"] == "Lab Coat"


def test_get_item_by_id_not_found(client: TestClient):
    response = client.get("/items/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ==========================================
# 4. PUT /items/{item_id} (Update Item Tests)
# ==========================================

def test_update_item_success(client: TestClient):
    res_create = client.post("/items", json={
        "title": "Car Keys",
        "description": "Honda car key with blue silicone fob",
        "category": "Accessories",
        "location": "North Parking Lot",
        "reported_by": "Campus Security",
        "status": "Found"
    })
    item_id = res_create.json()["id"]

    # Student collected item, update status to Returned
    update_payload = {
        "status": "Returned",
        "location": "Security Office (Handed over to owner)"
    }
    res_update = client.put(f"/items/{item_id}", json=update_payload)
    assert res_update.status_code == 200
    updated_data = res_update.json()
    assert updated_data["status"] == "Returned"
    assert updated_data["location"] == "Security Office (Handed over to owner)"
    assert updated_data["title"] == "Car Keys"


def test_update_item_not_found(client: TestClient):
    response = client.put("/items/99999", json={"status": "Returned"})
    assert response.status_code == 404


def test_update_item_invalid_data(client: TestClient):
    res_create = client.post("/items", json={
        "title": "Wallet",
        "description": "Brown leather bi-fold wallet",
        "category": "Accessories",
        "location": "Bus Stop",
        "reported_by": "Emma",
        "status": "Lost"
    })
    item_id = res_create.json()["id"]

    # Invalid empty title
    response = client.put(f"/items/{item_id}", json={"title": "  "})
    assert response.status_code == 422


# ==========================================
# 5. DELETE /items/{item_id} (Delete Item Tests)
# ==========================================

def test_delete_item_success(client: TestClient):
    res_create = client.post("/items", json={
        "title": "Water Bottle",
        "description": "Green insulated thermo flask",
        "category": "Accessories",
        "location": "Gym locker",
        "reported_by": "Sam",
        "status": "Lost"
    })
    item_id = res_create.json()["id"]

    # Delete
    res_del = client.delete(f"/items/{item_id}")
    assert res_del.status_code == 200
    assert "deleted" in res_del.json()["message"].lower()

    # Verify item no longer exists
    res_verify = client.get(f"/items/{item_id}")
    assert res_verify.status_code == 404


def test_delete_item_not_found(client: TestClient):
    response = client.delete("/items/99999")
    assert response.status_code == 404


# ==========================================
# 6. GET /items/status/{status} (Status Filter Tests)
# ==========================================

def test_filter_by_status(client: TestClient):
    client.post("/items", json={
        "title": "Headphones",
        "description": "Sony WH-1000XM4 noise cancelling headphones",
        "category": "Electronics",
        "location": "Study Pod 3",
        "reported_by": "Liam",
        "status": "Lost"
    })
    client.post("/items", json={
        "title": "Calculus Textbook",
        "description": "Stewart Calculus 8th Edition hardcover",
        "category": "Documents",
        "location": "Room 305",
        "reported_by": "Prof. Miller",
        "status": "Found"
    })

    # Test filtering Lost
    res_lost = client.get("/items/status/Lost")
    assert res_lost.status_code == 200
    data_lost = res_lost.json()
    assert len(data_lost) == 1
    assert data_lost[0]["title"] == "Headphones"

    # Test filtering Found
    res_found = client.get("/items/status/Found")
    assert res_found.status_code == 200
    data_found = res_found.json()
    assert len(data_found) == 1
    assert data_found[0]["title"] == "Calculus Textbook"

    # Test invalid status filter
    res_invalid = client.get("/items/status/Damaged")
    assert res_invalid.status_code == 400
    assert "invalid status" in res_invalid.json()["detail"].lower()


# ==========================================
# 7. GET /items/category/{category} (Category Filter Tests)
# ==========================================

def test_filter_by_category(client: TestClient):
    client.post("/items", json={
        "title": "iPad Pro",
        "description": "Apple iPad Pro 11 inch with Apple Pencil attached",
        "category": "Electronics",
        "location": "Seminar Hall",
        "reported_by": "David",
        "status": "Lost"
    })
    client.post("/items", json={
        "title": "Student ID Card",
        "description": "ID card with lanyard belonging to CS Department",
        "category": "Documents",
        "location": "Canteen",
        "reported_by": "Staff",
        "status": "Found"
    })

    # Category search Electronics (case-insensitive)
    res_elec = client.get("/items/category/Electronics")
    assert res_elec.status_code == 200
    assert len(res_elec.json()) == 1
    assert res_elec.json()[0]["title"] == "iPad Pro"

    # Lowercase category
    res_elec_lower = client.get("/items/category/electronics")
    assert res_elec_lower.status_code == 200
    assert len(res_elec_lower.json()) == 1

    # Documents category
    res_docs = client.get("/items/category/Documents")
    assert res_docs.status_code == 200
    assert len(res_docs.json()) == 1
    assert res_docs.json()[0]["title"] == "Student ID Card"
