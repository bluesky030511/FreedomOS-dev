# Copyright 2024 The Rubic. All Rights Reserved.
# ruff: noqa: ARG001


from faststream.annotations import Logger

from server import broker
from src.models import RobotBatchRequest, RobotScanRequest
from src.routers import robot_router


@robot_router.subscriber("scan_request")
async def mock_robot_scan_request_handler(
    body: RobotScanRequest, logger: Logger
) -> None: ...


@robot_router.subscriber("batch_request")
async def mock_robot_batch_request_handler(
    body: RobotBatchRequest, logger: Logger
) -> None: ...


broker.include_router(robot_router)
