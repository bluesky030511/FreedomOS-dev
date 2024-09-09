# Copyright 2024 The Rubic. All Rights Reserved.

"""Module containing serializers for database models."""

from __future__ import annotations

import uuid
from functools import cached_property
from typing import Annotated, Any, Literal, Protocol, TypeAlias

from bson import ObjectId
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_serializer,
)

# Helpers


def after_validate_object_id(v: Any) -> ObjectId | None:
    """Converts a string to an ObjectId if it is valid after validation."""
    if v is None:
        return None
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


def before_validate_object_id(v: Any) -> str | None:
    """Converts an ObjectId to a string before validation."""
    if v is None or v == "None":
        return None
    if isinstance(v, ObjectId):
        return str(v)
    if ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[
    str | None | ObjectId,
    AfterValidator(after_validate_object_id),
    BeforeValidator(before_validate_object_id),
]


class IsAbsolute(Protocol):
    """Protocol describing Absolute models."""

    @property
    def position(self) -> Vector3: ...  # noqa: D102

    @property
    def aligned_axis(self) -> str | None: ...  # noqa: D102


class IsRelative(Protocol):
    """Protocol describing Relative models."""

    @property
    def dimension(self) -> Vector3: ...  # noqa: D102


class CanHaveBoundingBox(Protocol):
    """Protocol describing models which implement the bounding_box property."""

    @property
    def absolute(self) -> IsAbsolute: ...  # noqa: D102
    @property
    def relative(self) -> IsRelative: ...  # noqa: D102


class BoundingBoxMixin:
    """Implement the bounding_box property."""

    @cached_property
    def bounding_box(self: CanHaveBoundingBox) -> Rectangle:
        """Model bounding box."""
        width, height, _ = self.relative.dimension.to_array()
        bottom_middle = self.absolute.position.model_dump()

        if self.absolute.aligned_axis is None:
            raise ValueError("Barcode missing aligned axis")

        bottom_left = Vector2(
            x=bottom_middle[self.absolute.aligned_axis] - (width / 2),
            y=bottom_middle["y"],
        )
        top_right = Vector2(
            x=bottom_middle[self.absolute.aligned_axis] + (width / 2),
            y=bottom_middle["y"] + height,
        )
        return Rectangle(bottom_left=bottom_left, top_right=top_right)


# Low level models


class Timestamp(BaseModel):
    """ROS timestamp."""

    sec: int
    nanosec: int


class Header(BaseModel):
    """ROS header."""

    stamp: Timestamp
    frame_id: str


class Vector3(BaseModel):
    """Vector3 model for ROS messages."""

    x: float
    y: float
    z: float = 0.0

    def to_array(self) -> list[float]:
        """Converts the vector to an array."""
        return [self.x, self.y, self.z]


class Vector2(BaseModel):
    """Vector2 model for ROS messages."""

    x: float
    y: float


class Rectangle(BaseModel):
    """Rectangle model."""

    bottom_left: Vector2
    top_right: Vector2

    @property
    def width(self) -> float:
        """Width of rectangle."""
        return self.top_right.x - self.bottom_left.x

    @property
    def height(self) -> float:
        """Height of rectangle."""
        return self.top_right.y - self.bottom_left.y


# Database models


class PartialItemMeta(BaseModel):
    """Partial item metadata."""

    item_type: str
    confidence: float
    image_id: PyObjectId | None = Field(default=None)
    scan_id: str
    aisle_index: int

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("image_id")
    @staticmethod
    def serialize_object_id(image_id: PyObjectId, _) -> str:  # noqa: ANN001
        """Method to serialize ObjectId to string."""
        return str(image_id)


class PartialItemAbsolute(BaseModel):
    """Partial item absolute to the box."""

    position: Vector3
    dimension: Vector3
    aligned_axis: Literal["x", "y", "z"]


class PartialItemRelative(BaseModel):
    """Partial item relative to the box."""

    header: Header
    position: Vector3
    dimension: Vector3
    side: Literal["left", "right"]


class PartialItem(BaseModel, BoundingBoxMixin):
    """Partial item (box, empty, or barcode are all items)."""

    object_id: PyObjectId | None = Field(default=None, alias="_id", exclude=True)
    meta: PartialItemMeta
    relative: PartialItemRelative
    absolute: PartialItemAbsolute

    model_config = ConfigDict(arbitrary_types_allowed=True)


class BarcodeMeta(BaseModel):
    """Barcode meta information."""

    barcode_type: str
    data: str
    scan_id: str | None = None
    image_id: PyObjectId | None = Field(default=None, exclude=True)
    aisle_index: int | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("image_id")
    @staticmethod
    def serialize_object_id(image_id: PyObjectId, _) -> str:  # noqa: ANN001
        """Method to serialize ObjectId to string."""
        return str(image_id)


class BarcodeAbsolute(BaseModel):
    """Barcode absolute position and dimension."""

    position: Vector3
    dimension: Vector3 | None = None
    aligned_axis: str | None = None


class BarcodeRelative(BaseModel):
    """Barcode relative position and dimension."""

    header: Header
    position: Vector3
    dimension: Vector3
    side: str


class Barcode(BaseModel, BoundingBoxMixin):
    """Barcode model."""

    object_id: PyObjectId | None = Field(default=None, alias="_id", exclude=True)
    meta: BarcodeMeta
    absolute: BarcodeAbsolute
    relative: BarcodeRelative
    item_uuid: str | None = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ItemAbsolute(BaseModel):
    """Item address."""

    depth_index: int | None = None
    stack_index: int | None = None
    position: Vector3
    dimension: Vector3 | None = Field(default=None, exclude=True)
    waypoint: str | None = None
    aligned_axis: str | None = Field(default=None)


class ItemRelative(BaseModel):
    """Item relative position and dimension."""

    header: Header | None = Field(default=None, exclude=True)
    position: Vector3 | None = Field(default=None, exclude=True)
    dimension: Vector3
    side: str


class ItemMeta(BaseModel):
    """Item meta information."""

    item_type: str | None = None
    stack: list[str] = []
    location: str | None = None
    destination: str | None = None
    available: bool = False
    aisle_index: int | None = None
    scan_id: str | None = None


class Item(BaseModel, BoundingBoxMixin):
    """Item model."""

    barcodes: list[Barcode] = []
    meta: ItemMeta
    absolute: ItemAbsolute
    relative: ItemRelative
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))

    object_id: PyObjectId | None = Field(default=None, alias="_id", exclude=True)

    # Only populated when sending to robot
    primary_barcode: Barcode | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ScanImage(BaseModel):
    """Scan image model."""

    image: str | None = None
    image_filename: str | None = None
    image_bottom_left: Vector3
    image_top_right: Vector3
    stamp: Timestamp
    scan_id: str
    side: Literal["left", "right"] | None = None


RobotJobType: TypeAlias = Literal[
    "FETCH_INVENTORY",
    "STORE_INVENTORY",
    "FETCH_DESIGNATED",
    "STORE_DESIGNATED",
]


class RobotJob(BaseModel):
    """Robot job model."""

    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_type: RobotJobType
    item: Item
    destination: Item | None = None
    future_uuid: str | None = None

    # optional fields
    attempted: bool | None = None
    success: bool | None = None
    error_code: int | None = None
    error_message: str | None = None


class JobType(BaseModel):
    """Job type model."""

    # DB - FOS_Translate
    # Collection - job_types

    job_type: str
    generic_type: str
    vendor: str
    predetermined: bool
    meta: ItemMeta | None = None
    absolute: ItemAbsolute | None = None
    item_uuid: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
