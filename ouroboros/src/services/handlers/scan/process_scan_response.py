# Copyright 2024 The Rubic. All Rights Reserved.

"""RobotScanResponse handler."""

from faststream.rabbit.annotations import Logger

from src.models import RobotScanResponse
from src.services.handlers import Handler


class ProcessRobotScanResponse(Handler):
    """RobotScanResponse handler."""

    async def run(self, body: RobotScanResponse, logger: Logger) -> None:  # noqa: PLR6301
        """Process RobotScanResponse message."""
        logger.info("Received scan completion callback with body {}", body)
