# Copyright 2024 The Rubic. All Rights Reserved.

"""Module for handling task request messages."""

from faststream.annotations import Logger
from faststream.rabbit.router import RabbitRouter

from src.decorators import log
from src.models import RenderScanRequest
from src.services.handlers.render import RenderInventory

inventory_router = RabbitRouter(prefix="inventory/")


@inventory_router.subscriber("render")
@log
async def render_request_handler(body: RenderScanRequest, logger: Logger) -> None:
    """Handle process request messages."""
    handler = RenderInventory()
    await handler.run(body, logger)
