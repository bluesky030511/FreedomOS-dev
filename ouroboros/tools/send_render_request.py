# Copyright 2024 The Rubic. All Rights Reserved.

"""Manually send a render request."""

import pika

from config import settings
from src.models import RenderScanRequest

if __name__ == "__main__":
    message = RenderScanRequest(
        vendor="NLS",
        user_id="",
        debug=False,
    )
    connection = pika.BlockingConnection(pika.URLParameters(settings.AMQP_CONN_STR))  # pyright: ignore[reportArgumentType]
    connection.channel().basic_publish(
        exchange="",
        routing_key="inventory/render",
        body=message.json(),
    )
