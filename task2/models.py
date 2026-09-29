from enum import Enum
from typing import Optional, List
from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship


class EventStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"


class EventBase(SQLModel):
    title: str = Field(min_length=1, max_length=200, description="Event name")
    venue: str = Field(min_length=1, max_length=200, description="Event location")
    capacity: int = Field(gt=0, description="Maximum number of participants (must be greater than 0)")
    organizer: str = Field(min_length=1, max_length=100, description="Organizer name")
    status: EventStatus = Field(default=EventStatus.OPEN, description="Event status: Open or Closed")

    @field_validator("title", "venue", "organizer", mode="before")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Field cannot be empty or blank")
            return v_stripped
        return v


class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    reservations: List["Reservation"] = Relationship(
        back_populates="event",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int


class EventUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    venue: Optional[str] = Field(default=None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(default=None, gt=0)
    organizer: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[EventStatus] = None

    @field_validator("title", "venue", "organizer", mode="before")
    @classmethod
    def validate_non_empty_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Field cannot be empty or blank")
            return v_stripped
        return v


class ReservationBase(SQLModel):
    student_name: str = Field(min_length=1, max_length=100, description="Participant name")
    roll_number: str = Field(min_length=1, max_length=50, description="Participant roll number")
    email: EmailStr = Field(description="Participant valid email address")

    @field_validator("student_name", "roll_number", mode="before")
    @classmethod
    def validate_non_empty_student_info(cls, v: str) -> str:
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("Field cannot be empty or blank")
            return v_stripped
        return v


class Reservation(ReservationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id", index=True, description="ID of the associated event")

    event: Optional[Event] = Relationship(back_populates="reservations")


class ReservationCreate(ReservationBase):
    pass


class ReservationRead(ReservationBase):
    id: int
    event_id: int


class AvailabilityResponse(SQLModel):
    capacity: int = Field(description="Total maximum participants")
    booked: int = Field(description="Number of current reservations")
    remaining: int = Field(description="Remaining available seats")
