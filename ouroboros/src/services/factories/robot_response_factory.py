# Copyright 2024 The Rubic. All Rights Reserved.

"""Module to implement factory pattern for producer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.services.robot_responses import (
    FetchDesignatedRobotResponse,
    FetchInventoryRobotResponse,
    StoreDesignatedRobotResponse,
    StoreInventoryRobotResponse,
)

if TYPE_CHECKING:
    from src.models.db import RobotJob
    from src.services.robot_responses.base_robot_response import RobotResponseABC


class RobotResponseFactory:
    """Implements factory design for robot responses."""

    @staticmethod
    def get_robot_response_service(job: RobotJob) -> RobotResponseABC:
        """Get robot response handler based on task type."""
        match job.job_type:
            case "FETCH_INVENTORY":
                return FetchInventoryRobotResponse()
            case "STORE_INVENTORY":
                return StoreInventoryRobotResponse()
            case "FETCH_DESIGNATED":
                return FetchDesignatedRobotResponse()
            case "STORE_DESIGNATED":
                return StoreDesignatedRobotResponse()
            case _:
                raise NotImplementedError(
                    f"Response with job type {job.job_type} is not supported"
                )
