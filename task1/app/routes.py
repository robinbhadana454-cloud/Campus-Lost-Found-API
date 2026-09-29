from typing import List
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlmodel import Session, select, func

from app.database import get_session
from app.models import Item, ItemCreate, ItemRead, ItemUpdate, ItemStatus

router = APIRouter(prefix="/items", tags=["Lost & Found Items"])


@router.post("", response_model=ItemRead, status_code=http_status.HTTP_201_CREATED, summary="Create a new lost/found item")
def create_item(
    item_in: ItemCreate,
    session: Session = Depends(get_session)
) -> Item:
    """
    Create a new report for a lost or found item.
    - **title**: Name or title of the item (required, non-empty)
    - **description**: Description containing meaningful text (min 3 chars)
    - **category**: Category e.g., Electronics, Documents, Accessories
    - **location**: Campus location where the item was lost/found
    - **reported_by**: Name of reporting student
    - **status**: Lost, Found, or Returned
    """
    db_item = Item.model_validate(item_in)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("", response_model=List[ItemRead], summary="Return all reported items")
def get_all_items(
    session: Session = Depends(get_session)
) -> List[Item]:
    """Retrieve all reported lost and found items stored in the SQLite database."""
    statement = select(Item).order_by(Item.id)
    items = session.exec(statement).all()
    return list(items)


@router.get("/status/{status}", response_model=List[ItemRead], summary="Filter items by status")
def get_items_by_status(
    status: str,
    session: Session = Depends(get_session)
) -> List[Item]:
    """
    Return items based on their status.
    Accepts: **Lost**, **Found**, or **Returned** (case-insensitive).
    """
    # Validate against allowed enum values
    matched_status: ItemStatus | None = None
    for s in ItemStatus:
        if s.value.lower() == status.strip().lower():
            matched_status = s
            break

    if not matched_status:
        allowed = [s.value for s in ItemStatus]
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{status}'. Permitted statuses are: {', '.join(allowed)}"
        )

    statement = select(Item).where(Item.status == matched_status).order_by(Item.id)
    items = session.exec(statement).all()
    return list(items)


@router.get("/category/{category}", response_model=List[ItemRead], summary="Filter items by category")
def get_items_by_category(
    category: str,
    session: Session = Depends(get_session)
) -> List[Item]:
    """
    Return all items belonging to a particular category (case-insensitive).
    Example: `/items/category/Electronics`
    """
    clean_category = category.strip()
    if not clean_category:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Category parameter must not be empty"
        )

    statement = select(Item).where(func.lower(Item.category) == clean_category.lower()).order_by(Item.id)
    items = session.exec(statement).all()
    return list(items)


@router.get("/{item_id}", response_model=ItemRead, summary="Get a specific item by ID")
def get_item(
    item_id: int,
    session: Session = Depends(get_session)
) -> Item:
    """
    Return a specific item using its ID.
    Returns HTTP 404 error if the item does not exist.
    """
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return item


@router.put("/{item_id}", response_model=ItemRead, summary="Update details/status of an existing item")
def update_item(
    item_id: int,
    item_update: ItemUpdate,
    session: Session = Depends(get_session)
) -> Item:
    """
    Update the details or status of an existing item report.
    Returns HTTP 404 error if the item does not exist.
    """
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )

    update_data = item_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update"
        )

    for field, val in update_data.items():
        setattr(db_item, field, val)

    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/{item_id}", summary="Delete an item report")
def delete_item(
    item_id: int,
    session: Session = Depends(get_session)
) -> dict:
    """
    Delete an item report by ID.
    Returns HTTP 404 error if the item does not exist.
    """
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )

    session.delete(db_item)
    session.commit()
    return {
        "message": f"Item with ID {item_id} successfully deleted",
        "deleted_id": item_id
    }
