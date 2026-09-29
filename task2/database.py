from sqlmodel import SQLModel, create_engine, Session

sqlite_file_name = "events.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False allows multiple threads (as in FastAPI requests) to interact with SQLite
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    echo=False
)

def create_db_and_tables():
    """Create all database tables defined in SQLModel metadata."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI dependency to provide a database session per request."""
    with Session(engine) as session:
        yield session
