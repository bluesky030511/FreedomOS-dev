# Copyright 2024 The Rubic. All Rights Reserved.

"""Job processing handler."""

from faststream.rabbit.annotations import Logger
from loguru import logger

from db.mongodb import (
    robot_batch_collection,
    robot_job_collection,
)
from src.models import (
    BatchRequest,
    RobotBatchRequest,
    RobotJob,
)
from src.services.factories import RobotJobFactory
from src.services.handlers import Handler


class ProcessBatchRequest(Handler):
    """Batch request handler."""

    async def run(self, body: BatchRequest, logger: Logger) -> RobotBatchRequest:
        """Handle batch request from client."""
        self.logger = logger
        self.logger.info("Received batch request with body {}", body)

        # TODO: Validate the batch

        return self.process_batch_request(body)

    def process_batch_request(self, batch_request: BatchRequest) -> RobotBatchRequest:
        """Process batch request."""
        logger.info("Processing batch request {}.", batch_request)

        # Convert batch into list of robot jobs
        robot_jobs: list[RobotJob] = []
        robot_job_factory = RobotJobFactory()
        for job_request in batch_request:
            jobs = robot_job_factory.build_jobs(job_request)
            robot_jobs.extend(jobs)

        robot_batch_request = RobotBatchRequest(jobs=robot_jobs)
        self.log_robot_batch_request(robot_batch_request)
        return robot_batch_request

    def log_robot_batch_request(self, robot_batch_request: RobotBatchRequest) -> None:
        """Send next RobotBatchRequest to robot."""
        # Insert robot request into db
        robot_batch_collection.insert_one(
            robot_batch_request.model_dump(exclude_none=True)
        )
        # Insert each job into db as well
        for robot_job in robot_batch_request.jobs:
            robot_job_collection.insert_one(robot_job.model_dump(exclude_none=True))

        self.logger.info(
            "Sending batch to robot with {} jobs.", len(robot_batch_request.jobs)
        )
