# Copyright 2024 The Rubic. All Rights Reserved.

from unittest.mock import patch

import pytest
from bson.objectid import ObjectId
from faststream.rabbit import TestRabbitBroker

from src.models import (
    Barcode,
    CompileScanDataRequest,
    PartialItem,
    ResultHeader,
    RobotScanResponse,
    ScanData,
    ScanRequest,
    Timestamp,
    Vector2,
)

from .mock_database import MOCK_CLIENT

with (
    patch("azure.keyvault.secrets.SecretClient"),
    patch("azure.storage.blob.BlobServiceClient"),
    patch("pymongo.MongoClient", return_value=MOCK_CLIENT),
    patch("config.settings.AMQP_CONN_STR", new=""),
):
    from db.mongodb import (
        partial_barcode_collection,
        partial_item_collection,
        scan_image_collection,
    )
    from server import broker
    from src.routers.scan import (
        compile_scan_data_handler,
        scan_data_handler,
        scan_request_handler,
        scan_response_handler,
    )

    from .mock_robot import mock_robot_scan_request_handler


@pytest.mark.asyncio
async def test_compile_scan_data() -> None:
    async with TestRabbitBroker(broker) as br:
        message = CompileScanDataRequest(
            vendor="NLS",
            user_id="258af564-80be-43f3-9638-77e5deb61467",
            confidence_threshold=0.15,
            scan_id="999f976a-1a1c-4d30-90e7-b6e770ce46a5",
            overwrite=True,
            aisle_index=35,
        )
        await br.publish(message=message, queue="scan/compile")

        # Validate received message
        handler_mock = compile_scan_data_handler.mock
        handler_mock.assert_called_with(message.model_dump())


@pytest.mark.asyncio
async def test_scan_request() -> None:
    async with TestRabbitBroker(broker) as br:
        message = ScanRequest(
            vendor="NLS",
            user_id="258af564-80be-43f3-9638-77e5deb61467",
            start_height=2.0,
            end_height=8.0,
            height_step=0.2,
            aisle_index=35,
            waypoint_start_index=100,
            waypoint_end_index=200,
            scan_id="xyz",
        )
        await br.publish(message=message, queue="scan/request")

        # Validate received message
        handler_mock = scan_request_handler.mock
        handler_mock.assert_called_with(message.model_dump())

        mock_robot_scan_request_handler.mock.assert_called_with(
            {
                "scan_id": "xyz",
                "start_height": 2.0,
                "end_height": 8.0,
                "height_step": 0.2,
                "aisle_index": 35,
                "waypoint_start_index": 100,
                "waypoint_end_index": 200,
                "waypoint_indices": [],
            }
        )


@pytest.mark.asyncio
async def test_scan_response() -> None:
    async with TestRabbitBroker(broker) as br:
        message = RobotScanResponse(
            header=ResultHeader(
                success=True, error_code=0, error_message="", safe_to_continue=True
            ),
        )
        await br.publish(message=message, queue="scan/response")

        # Validate received message
        handler_mock = scan_response_handler.mock
        handler_mock.assert_called_with(message.model_dump())


@pytest.mark.asyncio
async def test_ingest_scan_data() -> None:
    partial_barcode = partial_barcode_collection.find_one()
    partial_barcode = Barcode.model_validate(partial_barcode)

    partial_item = partial_item_collection.find_one()
    partial_item = PartialItem.model_validate(partial_item)

    scan_image = scan_image_collection.find_one(
        {"_id": ObjectId("662fc8daa7d34986e9fc9a26")}
    )

    async with TestRabbitBroker(broker) as br:
        message = ScanData(
            stamp=Timestamp(sec=0, nanosec=0),
            scan_id="xyz",
            side="left",
            image=scan_image["image"],
            aisle_index=35,
            image_bottom_left=Vector2(x=0, y=0),
            image_top_right=Vector2(x=1, y=1),
            image_filename="test.webp",
            partial_items=[partial_item],
            barcodes=[partial_barcode],
        )
        await br.publish(message=message, queue="scan/data")

        # Validate received message
        handler_mock = scan_data_handler.mock
        handler_mock.assert_called_with(message.model_dump())
