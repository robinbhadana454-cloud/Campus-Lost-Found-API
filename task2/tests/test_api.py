import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_session


# Use an in-memory SQLite database for isolated test execution
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# -------------------------------------------------------------
# EVENT APIS TESTS (1 to 5)
# -------------------------------------------------------------

def test_create_event_success(client: TestClient):
    """1. POST /events - Successfully create an event"""
    response = client.post(
        "/events",
        json={
            "title": "AI & Robotics Summit",
            "venue": "Auditorium Hall 1",
            "capacity": 50,
            "organizer": "Robotics Club",
            "status": "Open",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "AI & Robotics Summit"
    assert data["venue"] == "Auditorium Hall 1"
    assert data["capacity"] == 50
    assert data["organizer"] == "Robotics Club"
    assert data["status"] == "Open"


def test_get_events(client: TestClient):
    """2. GET /events - Return all events"""
    client.post(
        "/events",
        json={
            "title": "Hackathon 2026",
            "venue": "Lab 3",
            "capacity": 25,
            "organizer": "Coding Club",
            "status": "Open",
        },
    )
    client.post(
        "/events",
        json={
            "title": "Web Dev Workshop",
            "venue": "Seminar Hall",
            "capacity": 40,
            "organizer": "GDG Campus",
            "status": "Closed",
        },
    )

    response = client.get("/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 2
    assert events[0]["title"] == "Hackathon 2026"
    assert events[1]["title"] == "Web Dev Workshop"


def test_get_event_by_id(client: TestClient):
    """3. GET /events/{event_id} - Return a specific event"""
    create_res = client.post(
        "/events",
        json={
            "title": "Cybersecurity Conclave",
            "venue": "Auditorium 2",
            "capacity": 60,
            "organizer": "Cyber Cell",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    # Valid event
    res = client.get(f"/events/{event_id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Cybersecurity Conclave"

    # Non-existent event
    res_404 = client.get("/events/9999")
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()


def test_update_event(client: TestClient):
    """4. PUT /events/{event_id} - Update event information"""
    create_res = client.post(
        "/events",
        json={
            "title": "Cloud Computing 101",
            "venue": "Room 101",
            "capacity": 30,
            "organizer": "Cloud Club",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    # Update venue, capacity and status
    update_res = client.put(
        f"/events/{event_id}",
        json={
            "venue": "Grand Hall",
            "capacity": 45,
            "status": "Closed",
        },
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["venue"] == "Grand Hall"
    assert updated_data["capacity"] == 45
    assert updated_data["status"] == "Closed"
    assert updated_data["title"] == "Cloud Computing 101"  # Unchanged

    # Non-existent event
    res_404 = client.put("/events/9999", json={"title": "Ghost Event"})
    assert res_404.status_code == 404


def test_delete_event(client: TestClient):
    """5. DELETE /events/{event_id} - Delete an event and cascading reservations"""
    create_res = client.post(
        "/events",
        json={
            "title": "Design Thinking Seminar",
            "venue": "Room 205",
            "capacity": 20,
            "organizer": "Design Club",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    # Make a reservation first
    client.post(
        f"/events/{event_id}/reserve",
        json={
            "student_name": "Alice Smith",
            "roll_number": "CS-001",
            "email": "alice@college.edu",
        },
    )

    # Delete the event
    del_res = client.delete(f"/events/{event_id}")
    assert del_res.status_code == 200

    # Ensure event is deleted
    get_res = client.get(f"/events/{event_id}")
    assert get_res.status_code == 404

    # Delete non-existent event
    res_404 = client.delete("/events/9999")
    assert res_404.status_code == 404


# -------------------------------------------------------------
# RESERVATION APIS & APPLICATION LOGIC TESTS (6 to 9)
# -------------------------------------------------------------

def test_reserve_event_success(client: TestClient):
    """6. POST /events/{event_id}/reserve - Successful reservation creation"""
    create_res = client.post(
        "/events",
        json={
            "title": "Quantum Computing Basics",
            "venue": "Room 301",
            "capacity": 10,
            "organizer": "Physics Dept",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    res = client.post(
        f"/events/{event_id}/reserve",
        json={
            "student_name": "Bob Vance",
            "roll_number": "PHY-102",
            "email": "bob.vance@college.edu",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["event_id"] == event_id
    assert data["student_name"] == "Bob Vance"
    assert data["roll_number"] == "PHY-102"
    assert data["email"] == "bob.vance@college.edu"


def test_reserve_event_capacity_limit(client: TestClient):
    """Business Logic: Prevent exceeding defined capacity (e.g. capacity = 2)"""
    create_res = client.post(
        "/events",
        json={
            "title": "Micro Workshop",
            "venue": "Small Lab",
            "capacity": 2,
            "organizer": "Tech Lead",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    # 1st reservation -> Success
    res1 = client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "Student One", "roll_number": "R-1", "email": "s1@college.edu"},
    )
    assert res1.status_code == 201

    # 2nd reservation -> Success (now full: 2/2)
    res2 = client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "Student Two", "roll_number": "R-2", "email": "s2@college.edu"},
    )
    assert res2.status_code == 201

    # 3rd reservation -> Exceeds capacity, must be rejected with HTTP 400
    res3 = client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "Student Three", "roll_number": "R-3", "email": "s3@college.edu"},
    )
    assert res3.status_code == 400
    assert "full" in res3.json()["detail"].lower()


def test_reserve_closed_event(client: TestClient):
    """Business Logic: Prevent reservations when event is Closed"""
    create_res = client.post(
        "/events",
        json={
            "title": "Closed Seminar",
            "venue": "Hall A",
            "capacity": 50,
            "organizer": "Admin",
            "status": "Closed",
        },
    )
    event_id = create_res.json()["id"]

    res = client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "Eager Student", "roll_number": "R-99", "email": "eager@college.edu"},
    )
    assert res.status_code == 400
    assert "closed" in res.json()["detail"].lower()


def test_reserve_non_existent_event(client: TestClient):
    """Verify event exists before reserving (404)"""
    res = client.post(
        "/events/99999/reserve",
        json={"student_name": "Nobody", "roll_number": "R-00", "email": "nobody@college.edu"},
    )
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_get_event_reservations(client: TestClient):
    """7. GET /events/{event_id}/reservations - Return all reservations for an event"""
    create_res = client.post(
        "/events",
        json={
            "title": "Mobile App Development",
            "venue": "Lab 5",
            "capacity": 15,
            "organizer": "App Dev Club",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    # Add 2 reservations
    client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "Charlie", "roll_number": "CS-101", "email": "charlie@college.edu"},
    )
    client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "Diana", "roll_number": "CS-102", "email": "diana@college.edu"},
    )

    res = client.get(f"/events/{event_id}/reservations")
    assert res.status_code == 200
    reservations = res.json()
    assert len(reservations) == 2
    assert reservations[0]["student_name"] == "Charlie"
    assert reservations[1]["student_name"] == "Diana"

    # Non-existent event returns 404
    res_404 = client.get("/events/9999/reservations")
    assert res_404.status_code == 404


def test_cancel_reservation(client: TestClient):
    """8. DELETE /reservations/{reservation_id} - Cancel a reservation"""
    create_res = client.post(
        "/events",
        json={
            "title": "AI Workshop",
            "venue": "Room 404",
            "capacity": 10,
            "organizer": "AI Club",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    reserve_res = client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "Edward", "roll_number": "CS-201", "email": "edward@college.edu"},
    )
    reservation_id = reserve_res.json()["id"]

    # Delete / Cancel reservation
    del_res = client.delete(f"/reservations/{reservation_id}")
    assert del_res.status_code == 200
    assert "cancelled successfully" in del_res.json()["detail"].lower()

    # Now verify event availability freed up
    avail_res = client.get(f"/events/{event_id}/availability")
    assert avail_res.json()["booked"] == 0
    assert avail_res.json()["remaining"] == 10

    # Cancelling again -> 404
    del_res_again = client.delete(f"/reservations/{reservation_id}")
    assert del_res_again.status_code == 404


def test_event_availability(client: TestClient):
    """9. GET /events/{event_id}/availability - Total, booked, and remaining seats"""
    create_res = client.post(
        "/events",
        json={
            "title": "Campus Hackathon 2026",
            "venue": "Main Arena",
            "capacity": 50,
            "organizer": "Tech Fest Team",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    # Check initially empty
    res_initial = client.get(f"/events/{event_id}/availability")
    assert res_initial.status_code == 200
    assert res_initial.json() == {
        "capacity": 50,
        "booked": 0,
        "remaining": 50,
    }

    # Add 2 reservations
    client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "User 1", "roll_number": "U-1", "email": "u1@college.edu"},
    )
    client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "User 2", "roll_number": "U-2", "email": "u2@college.edu"},
    )

    # Check updated availability
    res_updated = client.get(f"/events/{event_id}/availability")
    assert res_updated.status_code == 200
    assert res_updated.json() == {
        "capacity": 50,
        "booked": 2,
        "remaining": 48,
    }

    # Non-existent event returns 404
    res_404 = client.get("/events/9999/availability")
    assert res_404.status_code == 404


# -------------------------------------------------------------
# VALIDATION TESTS
# -------------------------------------------------------------

def test_validation_capacity_must_be_greater_than_zero(client: TestClient):
    """Validation: Event capacity must be greater than 0"""
    res_zero = client.post(
        "/events",
        json={
            "title": "Zero Capacity Event",
            "venue": "Nowhere",
            "capacity": 0,
            "organizer": "Invalid",
            "status": "Open",
        },
    )
    assert res_zero.status_code == 422

    res_negative = client.post(
        "/events",
        json={
            "title": "Negative Capacity Event",
            "venue": "Nowhere",
            "capacity": -10,
            "organizer": "Invalid",
            "status": "Open",
        },
    )
    assert res_negative.status_code == 422


def test_validation_student_name_not_empty(client: TestClient):
    """Validation: Student name must not be empty"""
    create_res = client.post(
        "/events",
        json={
            "title": "DevOps BootCamp",
            "venue": "Lab 1",
            "capacity": 20,
            "organizer": "DevOps Guild",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    # Empty string
    res_empty = client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "", "roll_number": "CS-123", "email": "student@college.edu"},
    )
    assert res_empty.status_code == 422

    # Whitespace only
    res_whitespace = client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "   ", "roll_number": "CS-123", "email": "student@college.edu"},
    )
    assert res_whitespace.status_code == 422


def test_validation_email_format(client: TestClient):
    """Validation: Email must be validated"""
    create_res = client.post(
        "/events",
        json={
            "title": "Machine Learning Lab",
            "venue": "Lab 2",
            "capacity": 20,
            "organizer": "ML Club",
            "status": "Open",
        },
    )
    event_id = create_res.json()["id"]

    res_invalid_email = client.post(
        f"/events/{event_id}/reserve",
        json={"student_name": "Test Student", "roll_number": "CS-123", "email": "not-an-email"},
    )
    assert res_invalid_email.status_code == 422
