# Copyright 2024 The Rubic. All Rights Reserved.

"""Module containing the messages sent to robot."""

import uuid

from pydantic import BaseModel, Field

from .db import RobotJob


class RobotBatchRequest(BaseModel):
    """Model for robot batch request."""

    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jobs: list[RobotJob]


class RobotScanRequest(BaseModel):
    """Model for robot scan request."""

    scan_id: str
    start_height: float
    end_height: float
    height_step: float
    aisle_index: int
    waypoint_start_index: int = 0
    waypoint_end_index: int = 0
    waypoint_indices: list[int] = []
