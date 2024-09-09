# Copyright 2024 The Rubic. All Rights Reserved.

from unittest.mock import Mock, patch

import pytest
from faststream.rabbit import TestRabbitBroker

from src.models import Item, ResultHeader, RobotBatchResponse, RobotJob

from .mock_database import MOCK_CLIENT

with (
    patch("azure.keyvault.secrets.SecretClient"),
    patch("azure.storage.blob.BlobServiceClient"),
    patch("pymongo.MongoClient", return_value=MOCK_CLIENT),
    patch("config.settings.AMQP_CONN_STR", new=""),
):
    from db.mongodb import inventory_items, robot_batch_collection, robot_job_collection
    from server import broker
    from src.routers.batch import batch_response_handler


# Insert some fake data
robot_batch_collection.insert_one({"batch_id": "xyz"})
for i in range(10):
    robot_job_collection.insert_one({"job_id": f"j{i}"})


@pytest.mark.asyncio
async def test_empty_batch_response() -> None:
    async with TestRabbitBroker(broker) as br:
        message = RobotBatchResponse(
            batch_id="xyz",
            jobs=[],
            header=ResultHeader(
                success=True, error_code=0, error_message="", safe_to_continue=True
            ),
        )
        await br.publish(message=message, queue="batch/response")

        # Validate received message
        handler_mock = batch_response_handler.mock
        handler_mock.assert_called_with(message.model_dump())

    doc = robot_batch_collection.find_one({"batch_id": "xyz"})
    assert doc["header"]["success"] is True


@pytest.mark.asyncio
@patch("src.models.db.uuid.uuid4", return_value="abc0")
async def test_successful_fetch_inventory_response(_mock_uuid4: Mock) -> None:
    item = inventory_items.find_one({"uuid": "cc028893-860c-49d8-ae5a-0ce2f3f4cfb1"})
    item = Item.model_validate(item)
    item.primary_barcode = item.barcodes[0]

    async with TestRabbitBroker(broker) as br:
        message = RobotBatchResponse(
            batch_id="xyz",
            jobs=[
                RobotJob(
                    job_id="j0", job_type="FETCH_INVENTORY", item=item, success=True
                )
            ],
            header=ResultHeader(
                success=True, error_code=0, error_message="", safe_to_continue=True
            ),
        )
        await br.publish(message=message, queue="batch/response")

        # Validate received message
        handler_mock = batch_response_handler.mock
        handler_mock.assert_called_with(message.model_dump())

    doc = inventory_items.find_one({"uuid": "cc028893-860c-49d8-ae5a-0ce2f3f4cfb1"})
    assert doc["meta"]["location"] == "robot"

    doc = inventory_items.find_one({"uuid": "abc0"})
    assert doc["meta"]["item_type"] == "empty"


@pytest.mark.asyncio
async def test_successful_store_inventory_response() -> None:
    item = inventory_items.find_one({"uuid": "cc028893-860c-49d8-ae5a-0ce2f3f4cfb1"})
    item = Item.model_validate(item)
    item.primary_barcode = item.barcodes[0]
    destination = inventory_items.find_one({"uuid": "abc0"})

    assert destination is not None

    async with TestRabbitBroker(broker) as br:
        message = RobotBatchResponse(
            batch_id="xyz",
            jobs=[
                RobotJob(
                    job_id="j1",
                    job_type="STORE_INVENTORY",
                    item=item,
                    destination=destination,
                    success=True,
                )
            ],
            header=ResultHeader(
                success=True, error_code=0, error_message="", safe_to_continue=True
            ),
        )
        await br.publish(message=message, queue="batch/response")

        # Validate received message
        handler_mock = batch_response_handler.mock
        handler_mock.assert_called_with(message.model_dump())

    doc = inventory_items.find_one({"uuid": "cc028893-860c-49d8-ae5a-0ce2f3f4cfb1"})
    assert doc["meta"]["location"] == "inventory"

    doc = inventory_items.find_one({"uuid": "abc0"})
    assert doc is None


@pytest.mark.asyncio
@patch("src.services.robot_responses.fetch_designated.uuid.uuid4", return_value="abc1")
async def test_successful_fetch_designated_response(_mock_uuid4: Mock) -> None:
    item = inventory_items.find_one({"uuid": "32019050-0ff2-49e4-ab43-60c8367e2c15"})
    item = Item.model_validate(item)
    item.primary_barcode = item.barcodes[0]
    item.uuid = ""

    async with TestRabbitBroker(broker) as br:
        message = RobotBatchResponse(
            batch_id="xyz",
            jobs=[
                RobotJob(
                    job_id="j2", job_type="FETCH_DESIGNATED", item=item, success=True
                )
            ],
            header=ResultHeader(
                success=True, error_code=0, error_message="", safe_to_continue=True
            ),
        )
        await br.publish(message=message, queue="batch/response")

        # Validate received message
        handler_mock = batch_response_handler.mock
        handler_mock.assert_called_with(message.model_dump())

    doc = inventory_items.find_one({"uuid": "abc1"})
    assert doc["meta"]["location"] == "robot"


@pytest.mark.asyncio
async def test_successful_store_designated_response() -> None:
    item = inventory_items.find_one({"uuid": "abc1"})
    item = Item.model_validate(item)
    item.primary_barcode = item.barcodes[0]

    async with TestRabbitBroker(broker) as br:
        message = RobotBatchResponse(
            batch_id="xyz",
            jobs=[
                RobotJob(
                    job_id="j3", job_type="STORE_DESIGNATED", item=item, success=True
                )
            ],
            header=ResultHeader(
                success=True, error_code=0, error_message="", safe_to_continue=True
            ),
        )
        await br.publish(message=message, queue="batch/response")

        # Validate received message
        handler_mock = batch_response_handler.mock
        handler_mock.assert_called_with(message.model_dump())

    doc = inventory_items.find_one({"uuid": "abc1"})
    assert doc is None


@pytest.mark.asyncio
async def test_successful_store_designated_response_item_not_found() -> None:
    item = inventory_items.find_one({"uuid": "32019050-0ff2-49e4-ab43-60c8367e2c15"})
    item = Item.model_validate(item)
    item.primary_barcode = item.barcodes[0]
    item.uuid = "doesnotexist"

    async with TestRabbitBroker(broker) as br:
        message = RobotBatchResponse(
            batch_id="xyz",
            jobs=[
                RobotJob(
                    job_id="j3", job_type="STORE_DESIGNATED", item=item, success=True
                )
            ],
            header=ResultHeader(
                success=True, error_code=0, error_message="", safe_to_continue=True
            ),
        )
        with pytest.raises(
            ValueError,
            match='No item with uuid="doesnotexist" found in inventory_items',
        ):
            await br.publish(message=message, queue="batch/response")

        # Validate received message
        handler_mock = batch_response_handler.mock
        handler_mock.assert_called_with(message.model_dump())
