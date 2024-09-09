# Copyright 2024 The Rubic. All Rights Reserved.

"""Module containing the messages from client."""

from typing import Literal, TypeAlias
from uuid import uuid4

from pydantic import BaseModel, Field


class RenderScanRequest(BaseModel):
    """Pydantic model for render scan request."""

    vendor: str
    user_id: str
    item_type: str | None = None
    debug: bool | None = False


class JobRequest(BaseModel):
    """Pydantic model for job request."""

    job_type: str
    vendor: str
    uid: str | None = None
    destination_uuid: str | None = None
    request_id: str = Field(default_factory=lambda: str(uuid4()))


BatchRequest: TypeAlias = list[JobRequest]


class ScanRequest(BaseModel):
    """Pydantic model for scan request."""

    vendor: str
    user_id: str
    start_height: float
    end_height: float
    height_step: float
    aisle_index: int
    waypoint_start_index: int | None = None
    waypoint_end_index: int | None = None
    waypoint_indices: list[int] | None = None
    overwrite_scan_id: str | None = None
    scan_id: str = Field(default_factory=lambda: str(uuid4()))


class CompileScanDataRequest(BaseModel):
    """Pydantic model for compile scan data request."""

    vendor: str
    user_id: str
    item_type: str | None = None
    side: Literal["left", "right"] | None = None
    aisle_index: int | None = None
    scan_id: str
    confidence_threshold: float
    force: bool = False
    overwrite: bool = False
