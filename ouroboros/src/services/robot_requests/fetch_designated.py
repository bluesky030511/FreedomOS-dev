# Copyright 2024 The Rubic. All Rights Reserved.

"""Module to implement concrete fetch designated request."""

from __future__ import annotations

from src.models import RobotJob

from .base_robot_job_builder import RobotJobBuilderABC


class FetchDesignatedRobotJobBuilder(RobotJobBuilderABC):
    """Implements RobotJobBuilder for fetch designated jobs."""

    def build_jobs(self) -> list[RobotJob]:
        """Build fetch designated job."""
        pick_up_uuid = self.job_type.item_uuid

        if pick_up_uuid is None:
            raise ValueError(
                f"Job type {self.job_type.job_type} does "
                "not have a designated pick-up location"
            )

        item = self.get_item(pick_up_uuid)

        return [RobotJob(job_type="FETCH_DESIGNATED", item=item)]
