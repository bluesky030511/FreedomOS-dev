# Copyright 2024 The Rubic. All Rights Reserved.

"""Manually send a compile scan data request."""

import pika

from config import settings
from src.models import CompileScanDataRequest

if __name__ == "__main__":
    message = CompileScanDataRequest(
        vendor="NLS",
        user_id="",
        confidence_threshold=0.15,
        scan_id="47db912b-a9a3-4968-8259-9a27beb9a0fe",
        overwrite=True,
        aisle_index=69,
    )
    connection = pika.BlockingConnection(pika.URLParameters(settings.AMQP_CONN_STR))  # pyright: ignore[reportArgumentType]
    connection.channel().basic_publish(
        exchange="",
        routing_key="scan/compile",
        body=message.json(),
    )
