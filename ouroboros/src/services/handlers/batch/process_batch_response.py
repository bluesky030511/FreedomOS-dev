# Copyright 2024 The Rubic. All Rights Reserved.

"""Batch response handler."""

from faststream.rabbit.annotations import Logger
from loguru import logger

from db.mongodb import robot_batch_collection
from src.models import ItemUpdate, RobotBatchResponse
from src.services.factories import RobotResponseFactory
from src.services.handlers import Handler


class ProcessBatchResponse(Handler):
    """Batch response handler."""

    async def run(self, body: RobotBatchResponse, logger: Logger) -> list[ItemUpdate]:
        """Handle robot response."""
        logger.info("Received batch response with body {}", body)
        response = body

        # TODO: Validate the response

        if response.header.success:
            logger.info(
                "Robot successfully completed batch {} with {} jobs",
                response.batch_id,
                len(response.jobs),
            )
        else:
            logger.error("Robot failed to complete batch {}", response.batch_id)
            for job in response.jobs:
                logger.error(
                    "[{}] - [{}] | {}",
                    job.job_id,
                    job.success,
                    job.error_message,
                )

        return self.process_response(response)

    @staticmethod
    def process_response(response: RobotBatchResponse) -> list[ItemUpdate]:
        """Process response."""
        updates = []
        # Update the db
        robot_batch_collection.replace_one(
            {"batch_id": response.batch_id}, response.model_dump()
        )

        for job in response.jobs:
            response_service = RobotResponseFactory.get_robot_response_service(job)
            response_service.process(job)
            updates.extend(response_service.updates)

        logger.info(
            "Processed batch {} with {} jobs", response.batch_id, len(response.jobs)
        )

        return updates
