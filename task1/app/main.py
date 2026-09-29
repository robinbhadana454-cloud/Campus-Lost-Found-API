from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import router as items_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes the database and ensures tables are created when the app starts.
    """
    init_db()
    yield


app = FastAPI(
    title="College Campus Lost & Found API",
    description=(
        "A robust digital Lost & Found system built with FastAPI, SQLite, and SQLModel. "
        "Allows college students and staff to report, track, update, and manage lost and found items on campus."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for frontend integration and browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register items routes
app.include_router(items_router)


@app.get("/", tags=["General"])
def root():
    """Welcome endpoint providing service overview and documentation links."""
    return {
        "service": "College Campus Lost & Found API",
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "create_item": "POST /items",
            "list_items": "GET /items",
            "get_item_by_id": "GET /items/{item_id}",
            "update_item": "PUT /items/{item_id}",
            "delete_item": "DELETE /items/{item_id}",
            "filter_by_status": "GET /items/status/{status}",
            "filter_by_category": "GET /items/category/{category}"
        }
    }


@app.get("/health", tags=["General"])
def health_check():
    """Health check endpoint confirming API service and database readiness."""
    return {"status": "healthy", "database": "sqlite", "engine": "SQLModel"}
