# Copyright 2024 The Rubic. All Rights Reserved.

"""Manually send a batch request."""

import json

import pika

from config import settings
from src.models import JobRequest

if __name__ == "__main__":
    jobs = [
        # Fetch
        JobRequest(
            job_type="FETCH_INVENTORY",
            vendor="RUBIC",
            uid="00008466220588549083",
            destination_uuid="fetch1",
        ),
        JobRequest(
            job_type="FETCH_INVENTORY",
            vendor="RUBIC",
            uid="00008466220588549014",
            destination_uuid="fetch2",
        ),
        # JobRequest(
        #     job_type="FETCH_INVENTORY",
        #     vendor="RUBIC",
        #     uid="00100897774116673704",
        #     destination_uuid="fetch3",
        # ),
        # JobRequest(
        #     job_type="FETCH_INVENTORY",
        #     vendor="RUBIC",
        #     uid="00100897774116673667",
        #     destination_uuid="fetch4",
        # ),
        # # Drop-off
        # JobRequest(
        #     job_type="INT2",
        #     vendor="NLS",
        #     uid="x",
        # ),
        # JobRequest(
        #     job_type="INT2",
        #     vendor="NLS",
        #     uid="x",
        # ),
        # JobRequest(
        #     job_type="INT2",
        #     vendor="NLS",
        #     uid="x",
        # ),
        # # Pick-up
        # JobRequest(
        #     job_type="INT1",
        #     vendor="NLS",
        # ),
        # JobRequest(
        #     job_type="INT1",
        #     vendor="NLS",
        # ),
        # JobRequest(
        #     job_type="INT1",
        #     vendor="NLS",
        # ),
        # # Store
        JobRequest(
            job_type="STORE_INVENTORY",
            vendor="RUBIC",
            uid="00008466220588549083",
            destination_uuid="00008466220588549014",
        ),
        JobRequest(
            job_type="STORE_INVENTORY",
            vendor="RUBIC",
            uid="00008466220588549014",
            destination_uuid="00008466220588549083",
        ),
        # JobRequest(
        #     job_type="STORE_INVENTORY",
        #     vendor="RUBIC",
        #     uid="00100897774116673667",
        #     destination_uuid="00100897774116673667",
        # ),
        # JobRequest(
        #     job_type="STORE_INVENTORY",
        #     vendor="RUBIC",
        #     uid="00100897774116673704",
        #     destination_uuid="00100897774116673704",
        # ),
    ]
    message = [job.model_dump() for job in jobs]
    message = json.dumps(message)
    connection = pika.BlockingConnection(pika.URLParameters(settings.AMQP_CONN_STR))  # pyright: ignore[reportArgumentType]
    connection.channel().basic_publish(
        exchange="",
        routing_key="batch/request",
        body=message,
    )
