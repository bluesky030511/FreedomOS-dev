# Copyright 2024 The Rubic. All Rights Reserved.

"""Module to implement factory pattern for robot job builders."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from loguru import logger

from db.mongodb import job_type_collection
from src.models import JobType, RobotJob
from src.services.robot_requests import (
    FetchDesignatedRobotJobBuilder,
    FetchInventoryRobotJobBuilder,
    StoreDesignatedRobotJobBuilder,
    StoreInventoryRobotJobBuilder,
)

if TYPE_CHECKING:
    from src.models import JobRequest
    from src.services.robot_requests.base_robot_job_builder import RobotJobBuilderABC


@functools.lru_cache
def get_job_type(vendor: str, job_type: str) -> JobType:
    """Get job_type object."""
    job_type_doc = job_type_collection.find_one(
        {
            "vendor": vendor,
            "job_type": job_type,
        },
    )
    if job_type_doc is None:
        msg = f"Job type {job_type} not found for vendor {vendor}"
        logger.error(msg)
        raise ValueError(msg)

    return JobType.model_validate(job_type_doc)


class RobotJobFactory:
    """Implements factory design for robot job builders."""

    def __init__(self):
        """Initialize the RobotJobBuilderFactory class."""
        self.fetched_items = {}

    def build_jobs(self, job_request: JobRequest) -> list[RobotJob]:
        """Build jobs to accomplish job_request."""
        job_type = get_job_type(job_request.vendor, job_request.job_type)
        job_builder = self.get_robot_job_builder(job_request, job_type)
        jobs = job_builder.build_jobs()

        if job_type.generic_type == "FETCH_INVENTORY":
            self.fetched_items[job_request.uid] = job_request.destination_uuid

        return jobs

    def get_robot_job_builder(
        self, job_request: JobRequest, job_type: JobType
    ) -> RobotJobBuilderABC:
        """Get robot job builder based on job type."""
        if job_type.generic_type == "FETCH_INVENTORY":
            return FetchInventoryRobotJobBuilder(
                job_request, job_type, self.fetched_items
            )

        if job_type.generic_type == "STORE_INVENTORY":
            return StoreInventoryRobotJobBuilder(
                job_request, job_type, self.fetched_items
            )

        if job_type.generic_type == "STORE_DESIGNATED":
            return StoreDesignatedRobotJobBuilder(
                job_request, job_type, self.fetched_items
            )

        if job_type.generic_type == "FETCH_DESIGNATED":
            return FetchDesignatedRobotJobBuilder(
                job_request, job_type, self.fetched_items
            )

        raise ValueError(f"Job type {job_type.generic_type} is not supported")
