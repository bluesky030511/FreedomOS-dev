# Copyright 2024 The Rubic. All Rights Reserved.

"""Models for rendering inventory items."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, computed_field

from src.models import Item, RenderScanRequest


class RenderItemData(BaseModel):
    """Pydantic model for render item data."""

    item: Item
    x0: float
    y0: float
    x1: float
    y1: float


class RenderMeta(BaseModel):
    """Pydantic model for render meta."""

    side: str
    aisle_index: int


class RenderImageMeta(BaseModel):
    """Pydantic model for render image meta."""

    x: float
    y: float
    width: float
    height: float
    container_name: str | None = None
    blob_name: str | None = None


class Render(BaseModel):
    """Pydantic model for render."""

    request: RenderScanRequest
    meta: RenderMeta
    data: list[RenderItemData]
    img_meta: RenderImageMeta | None = None

    @computed_field
    @property
    def created_at_utc(self) -> float:
        """Get the current timestamp."""
        return datetime.now(UTC).timestamp()


class ItemUpdate(BaseModel):
    """Pydantic model for item update."""

    change: Literal["CREATED", "UPDATED", "DELETED"]
    item: Item
