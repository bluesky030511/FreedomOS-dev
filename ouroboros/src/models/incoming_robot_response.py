# Copyright 2024 The Rubic. All Rights Reserved.

"""Module containing the messages from robot."""

from typing import Literal

from pydantic import BaseModel

from .db import Barcode, PartialItem, RobotJob, Timestamp, Vector2


class ResultHeader(BaseModel):
    """Result header indicating success and error."""

    success: bool
    error_code: int
    error_message: str
    safe_to_continue: bool


class RobotBatchResponse(BaseModel):
    """Pydantic model for robot batch response."""

    batch_id: str
    jobs: list[RobotJob]
    header: ResultHeader


class RobotScanResponse(BaseModel):
    """Pydantic model for robot scan response."""

    header: ResultHeader


class ScanData(BaseModel):
    """Pydantic model for scan data."""

    stamp: Timestamp
    scan_id: str
    side: Literal["left", "right"]
    image: str
    aisle_index: int
    image_bottom_left: Vector2
    image_top_right: Vector2
    image_filename: str
    partial_items: list[PartialItem]
    barcodes: list[Barcode]
