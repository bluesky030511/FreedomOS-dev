# Copyright 2024 The Rubic. All Rights Reserved.

"""Module for handling task request messages."""

from faststream.annotations import Logger
from faststream.rabbit.router import RabbitRouter

from src.decorators import log
from src.models import (
    CompileScanDataRequest,
    RobotScanRequest,
    RobotScanResponse,
    ScanData,
    ScanRequest,
)
from src.services.handlers.scan import (
    CompileScanData,
    IngestScanData,
    ProcessRobotScanResponse,
    ProcessScanRequest,
)

from .robot import robot_router

scan_router = RabbitRouter(prefix="scan/")


@scan_router.subscriber("request")
@robot_router.publisher("scan_request")
@log
async def scan_request_handler(body: ScanRequest, logger: Logger) -> RobotScanRequest:
    """Handle scan request."""
    handler = ProcessScanRequest()
    return await handler.run(body, logger)


@scan_router.subscriber("response")
@log
async def scan_response_handler(body: RobotScanResponse, logger: Logger) -> None:
    """Handle scan response."""
    handler = ProcessRobotScanResponse()
    await handler.run(body, logger)


@scan_router.subscriber("compile")
@log
async def compile_scan_data_handler(
    body: CompileScanDataRequest, logger: Logger
) -> None:
    """Handle compile scan data request."""
    handler = CompileScanData(body)
    await handler.run(logger)


@scan_router.subscriber("data")
@log
async def scan_data_handler(body: ScanData, logger: Logger) -> None:
    """Handle scan data message."""
    handler = IngestScanData()
    await handler.run(body, logger)
