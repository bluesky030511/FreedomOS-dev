# Copyright 2024 The Rubic. All Rights Reserved.

"""Main file."""

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from loguru import logger

from config import settings
from src.routers import batch_router, inventory_router, robot_router, scan_router

broker = RabbitBroker(settings.AMQP_CONN_STR, logger=logger)

app = FastStream(broker, logger=logger)

broker.include_router(batch_router)
broker.include_router(inventory_router)
broker.include_router(robot_router)
broker.include_router(scan_router)
