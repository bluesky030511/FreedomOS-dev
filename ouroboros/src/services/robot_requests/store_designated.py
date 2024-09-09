# Copyright 2024 The Rubic. All Rights Reserved.

"""Module to implement concrete store designated job builder."""

from __future__ import annotations

from src.models import RobotJob

from .base_robot_job_builder import RobotJobBuilderABC


class StoreDesignatedRobotJobBuilder(RobotJobBuilderABC):
    """Implements RobotJobBuilder for store designated jobs."""

    def build_jobs(self) -> list[RobotJob]:
        """Build store designated job."""
        item = self.get_item_from_barcode(self.request.uid)
        destination_uuid = self.job_type.item_uuid
        if destination_uuid is None:
            raise ValueError(
                f"Job type {self.job_type.job_type} does "
                "not have a designated destination"
            )
        destination = self.get_item(destination_uuid)
        return [
            RobotJob(
                job_type="STORE_DESIGNATED",
                item=item,
                destination=destination,
            )
        ]
