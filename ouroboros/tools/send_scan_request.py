# Copyright 2024 The Rubic. All Rights Reserved.

"""Manually send a scan request."""

import pika

from config import settings
from src.models import ScanRequest

if __name__ == "__main__":
    message = ScanRequest(
        vendor="NLS",
        user_id="",
        start_height=2.0,
        end_height=9.0,
        height_step=0.2,
        aisle_index=69,
        waypoint_start_index=749,
        waypoint_end_index=745,
        overwrite_scan_id="47db912b-a9a3-4968-8259-9a27beb9a0fe",
    )
    connection = pika.BlockingConnection(pika.URLParameters(settings.AMQP_CONN_STR))  # pyright: ignore[reportArgumentType]
    connection.channel().basic_publish(
        exchange="",
        routing_key="scan/request",
        body=message.json(),
    )
