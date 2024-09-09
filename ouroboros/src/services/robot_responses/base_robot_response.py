# Copyright 2024 The Rubic. All Rights Reserved.

"""Implements abstract class for robot response processing."""

from abc import ABC, abstractmethod

from loguru import logger

from db.mongodb import robot_job_collection
from src.models import ItemUpdate, RobotJob


class RobotResponseABC(ABC):
    """Abstract class for response processing."""

    job_type: str

    def __init__(self):
        """Initialize the RobotResponse class."""
        self.updates: list[ItemUpdate] = []

    def process(self, job: RobotJob) -> None:
        """Process job."""
        if job.item.primary_barcode is None:
            raise ValueError("Response missing primary barcode")

        if job.success:
            logger.info(
                "Robot successfully {}ed item {}",
                self.job_type,
                job.item.primary_barcode.meta.data,
            )

            # Get the job from the database and update it
            robot_job_collection.replace_one({"job_id": job.job_id}, job.model_dump())

            self.update_inventory(job)

        else:
            logger.error(
                'Robot failed to {} item {} with error "{}".',
                self.job_type,
                job.item.primary_barcode.meta.data,
                job.error_message,
            )

    @abstractmethod
    def update_inventory(self, job: RobotJob) -> None:
        """Update items in inventory."""
        raise NotImplementedError
