from enum import Enum
from typing import Optional
from pydantic import field_validator
from sqlmodel import Field, SQLModel


class ItemStatus(str, Enum):
    """Permitted statuses for Lost & Found items."""
    LOST = "Lost"
    FOUND = "Found"
    RETURNED = "Returned"


class ItemBase(SQLModel):
    """Base schema for Lost & Found items with comprehensive validation."""
    title: str = Field(
        min_length=1,
        max_length=150,
        description="Name or title of the item (cannot be empty)",
        schema_extra={"examples": ["Blue HP Laptop"]}
    )
    description: str = Field(
        min_length=3,
        max_length=1000,
        description="Detailed description with meaningful text",
        schema_extra={"examples": ["HP Pavilion 15-inch laptop inside a grey neoprene sleeve with stickers on lid"]}
    )
    category: str = Field(
        min_length=1,
        max_length=100,
        description="Category such as Electronics, Documents, Accessories, etc.",
        schema_extra={"examples": ["Electronics"]}
    )
    location: str = Field(
        min_length=1,
        max_length=200,
        description="Location where the item was lost or found",
        schema_extra={"examples": ["Library 2nd Floor Reading Room"]}
    )
    reported_by: str = Field(
        min_length=1,
        max_length=100,
        description="Name of the student/person reporting it",
        schema_extra={"examples": ["Alex Johnson"]}
    )
    status: ItemStatus = Field(
        default=ItemStatus.LOST,
        description="Item status: Lost, Found, or Returned",
        schema_extra={"examples": ["Lost"]}
    )

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError("title must not be empty or blank")
            return v_stripped
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if isinstance(v, str):
            v_stripped = v.strip()
            if len(v_stripped) < 3:
                raise ValueError("description must contain meaningful text (minimum 3 characters)")
            return v_stripped
        return v

    @field_validator("category", "location", "reported_by", mode="before")
    @classmethod
    def validate_non_empty_strings(cls, v: str, info) -> str:
        if isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError(f"{info.field_name} must not be empty or blank")
            return v_stripped
        return v


class Item(ItemBase, table=True):
    """Database model for storing items in SQLite via SQLModel."""
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)


class ItemCreate(ItemBase):
    """Request schema for creating a new item."""
    pass


class ItemRead(ItemBase):
    """Response schema returning item details including generated ID."""
    id: int


class ItemUpdate(SQLModel):
    """Request schema for updating an existing item."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, min_length=3, max_length=1000)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    reported_by: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[ItemStatus] = Field(default=None)

    @field_validator("title", "category", "location", "reported_by", mode="before")
    @classmethod
    def validate_optional_non_empty(cls, v: Optional[str], info) -> Optional[str]:
        if v is not None and isinstance(v, str):
            v_stripped = v.strip()
            if not v_stripped:
                raise ValueError(f"{info.field_name} cannot be empty or blank")
            return v_stripped
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_optional_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            v_stripped = v.strip()
            if len(v_stripped) < 3:
                raise ValueError("description must contain meaningful text (minimum 3 characters)")
            return v_stripped
        return v
