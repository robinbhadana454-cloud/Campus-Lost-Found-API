from typing import Generator
import os
from sqlmodel import SQLModel, Session, create_engine

DATABASE_FILE = "lost_and_found.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_FILE}")

# SQLite requires check_same_thread=False when used with multithreaded servers like FastAPI
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# Create the database engine using create_engine() as required
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Initialize database tables according to SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency to yield database sessions with safe teardown."""
    with Session(engine) as session:
        yield session
