# Copyright 2024 The Rubic. All Rights Reserved.

from unittest.mock import MagicMock, patch

import pytest
from faststream.log import logger
from faststream.rabbit import TestRabbitBroker

from .mock_database import MOCK_CLIENT

with (
    patch("azure.keyvault.secrets.SecretClient"),
    patch("azure.storage.blob.BlobServiceClient"),
    patch("pymongo.MongoClient", return_value=MOCK_CLIENT),
    patch("config.settings.AMQP_CONN_STR", new=""),
):
    from server import broker
    from src.models import RenderScanRequest
    from src.routers.inventory import render_request_handler


@pytest.mark.asyncio
async def test_render_scan_request() -> None:
    """Test render scan request."""
    async with TestRabbitBroker(broker) as br:
        message = RenderScanRequest(
            vendor="NLS", user_id="258af564-80be-43f3-9638-77e5deb61467", debug=False
        )
        await br.publish(message=message, queue="inventory/render")
        # magic mock the handler
        mock: MagicMock | None = render_request_handler.mock
        mock.assert_called_with(message.model_dump())

        logger.info("Completed message")
