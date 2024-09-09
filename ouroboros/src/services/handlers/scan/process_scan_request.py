# Copyright 2024 The Rubic. All Rights Reserved.

"""ScanRequest handler."""

from faststream.rabbit.annotations import Logger

from src.models import RobotScanRequest, ScanRequest
from src.services.handlers import Handler


class ProcessScanRequest(Handler):
    """ScanRequest handler."""

    async def run(self, body: ScanRequest, logger: Logger) -> RobotScanRequest:  # noqa: PLR6301
        """Process ScanRequest message."""
        request = body

        logger.info("Received scan request {}", request)

        if request.overwrite_scan_id:
            request.scan_id = request.overwrite_scan_id

        scan_request_data = request.model_dump(
            exclude={"vendor", "user_id", "request_at_utc", "overwrite_scan_id"},
            exclude_none=True,
        )
        robot_request = RobotScanRequest.model_validate(scan_request_data)
        logger.info("Sending scan request to robot. {}", robot_request)

        return robot_request
