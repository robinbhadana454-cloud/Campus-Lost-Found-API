from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from database import get_session
from models import (
    Event,
    EventCreate,
    EventRead,
    EventUpdate,
    EventStatus,
    Reservation,
    ReservationCreate,
    ReservationRead,
    AvailabilityResponse,
)

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    session: Session = Depends(get_session)
):
    """
    1. POST /events
    Create a new event.
    """
    db_event = Event.model_validate(event_data)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router.get("", response_model=List[EventRead], status_code=status.HTTP_200_OK)
def list_events(
    session: Session = Depends(get_session)
):
    """
    2. GET /events
    Return all events.
    """
    events = session.exec(select(Event)).all()
    return events


@router.get("/{event_id}", response_model=EventRead, status_code=status.HTTP_200_OK)
def get_event(
    event_id: int,
    session: Session = Depends(get_session)
):
    """
    3. GET /events/{event_id}
    Return a specific event.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    return event


@router.put("/{event_id}", response_model=EventRead, status_code=status.HTTP_200_OK)
def update_event(
    event_id: int,
    event_update: EventUpdate,
    session: Session = Depends(get_session)
):
    """
    4. PUT /events/{event_id}
    Update event information.
    """
    db_event = session.get(Event, event_id)
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)

    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(
    event_id: int,
    session: Session = Depends(get_session)
):
    """
    5. DELETE /events/{event_id}
    Delete an event and its associated reservations.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    # Delete related reservations explicitly for clarity and SQLite safety
    reservations = session.exec(
        select(Reservation).where(Reservation.event_id == event_id)
    ).all()
    for res in reservations:
        session.delete(res)

    session.delete(event)
    session.commit()
    return {"detail": f"Event {event_id} and associated reservations deleted successfully"}


@router.post(
    "/{event_id}/reserve",
    response_model=ReservationRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Reservations"]
)
def reserve_event(
    event_id: int,
    reservation_data: ReservationCreate,
    session: Session = Depends(get_session)
):
    """
    6. POST /events/{event_id}/reserve
    Create a reservation for an event.
    
    Verifications:
    • Verify that the event exists.
    • Verify that the event is Open.
    • Check the number of existing reservations.
    • Do not allow reservations if the event is already full.
    """
    # 1. Verify that the event exists
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    # 2. Verify that the event is Open
    if event.status != EventStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reserve: Event '{event.title}' is currently {event.status}. Reservations are closed."
        )

    # 3. Check number of existing reservations
    booked_count = session.exec(
        select(func.count()).select_from(Reservation).where(Reservation.event_id == event_id)
    ).one()

    # 4. Check if event is already full
    if booked_count >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reserve: Event '{event.title}' is full. Capacity of {event.capacity} reached."
        )

    # Create reservation
    reservation = Reservation(
        event_id=event_id,
        student_name=reservation_data.student_name,
        roll_number=reservation_data.roll_number,
        email=reservation_data.email
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.get(
    "/{event_id}/reservations",
    response_model=List[ReservationRead],
    status_code=status.HTTP_200_OK,
    tags=["Reservations"]
)
def get_event_reservations(
    event_id: int,
    session: Session = Depends(get_session)
):
    """
    7. GET /events/{event_id}/reservations
    Return all reservations for a particular event.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    reservations = session.exec(
        select(Reservation).where(Reservation.event_id == event_id)
    ).all()
    return reservations


@router.get(
    "/{event_id}/availability",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_200_OK,
    tags=["Reservations"]
)
def get_event_availability(
    event_id: int,
    session: Session = Depends(get_session)
):
    """
    9. GET /events/{event_id}/availability
    Return the number of total seats, booked seats and remaining seats.
    """
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    booked_count = session.exec(
        select(func.count()).select_from(Reservation).where(Reservation.event_id == event_id)
    ).one()

    remaining_seats = max(0, event.capacity - booked_count)

    return AvailabilityResponse(
        capacity=event.capacity,
        booked=booked_count,
        remaining=remaining_seats
    )
