# Copyright 2024 The Rubic. All Rights Reserved.

"""Module for handling task request messages."""

from faststream.annotations import Logger
from faststream.rabbit.router import RabbitRouter

from src.decorators import log
from src.models import BatchRequest, ItemUpdate, RobotBatchRequest, RobotBatchResponse
from src.services.handlers.batch import ProcessBatchRequest, ProcessBatchResponse

from .inventory import inventory_router
from .robot import robot_router

batch_router = RabbitRouter(prefix="batch/")


@batch_router.subscriber("request")
@robot_router.publisher("batch_request")
@log
async def batch_request_handler(
    body: BatchRequest, logger: Logger
) -> RobotBatchRequest:
    """Handle batch request."""
    handler = ProcessBatchRequest()
    return await handler.run(body, logger)


@batch_router.subscriber("response")
@inventory_router.publisher("updates")
@log
async def batch_response_handler(
    body: RobotBatchResponse, logger: Logger
) -> list[ItemUpdate]:
    """Handle batch response."""
    handler = ProcessBatchResponse()
    return await handler.run(body, logger)
