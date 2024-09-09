# Copyright 2024 The Rubic. All Rights Reserved.

from unittest.mock import patch

import pytest
from faststream.rabbit import TestRabbitBroker

from .mock_database import MOCK_CLIENT

with (
    patch("azure.keyvault.secrets.SecretClient"),
    patch("azure.storage.blob.BlobServiceClient"),
    patch("pymongo.MongoClient", return_value=MOCK_CLIENT),
    patch("config.settings.AMQP_CONN_STR", new=""),
):
    from server import broker
    from src.models import JobRequest
    from src.routers.batch import batch_request_handler

    from .mock_robot import mock_robot_batch_request_handler


@pytest.mark.asyncio
async def test_fetch_inventory() -> None:
    async with TestRabbitBroker(broker) as br:
        message = [
            JobRequest(
                job_type="FETCH_INVENTORY",
                vendor="RUBIC",
                uid="00100897774117552794",
            )
        ]
        await br.publish(message=message, queue="batch/request")

        # Validate received message
        batch_request_handler.mock.assert_called_with(
            [job.model_dump() for job in message]
        )

        # Validate sent message
        call_args = mock_robot_batch_request_handler.mock.call_args_list
        assert len(call_args) == 1
        (sent_message,), _ = call_args[0]
        assert len(sent_message["jobs"]) == 1
        job = sent_message["jobs"][0]
        assert job["job_type"] == "FETCH_INVENTORY"
        assert job["item"]["uuid"] == "c4440f6a-7638-4872-91a2-7be10db915aa"


@pytest.mark.asyncio
async def test_fetch_inventory_stacked() -> None:
    async with TestRabbitBroker(broker) as br:
        message = [
            JobRequest(
                job_type="FETCH_INVENTORY",
                vendor="RUBIC",
                uid="00100897774116019311",
            )
        ]
        await br.publish(message=message, queue="batch/request")

        # Validate received message
        batch_request_handler.mock.assert_called_with(
            [job.model_dump() for job in message]
        )

        # Validate sent message
        call_args = mock_robot_batch_request_handler.mock.call_args_list
        assert len(call_args) == 1
        (sent_message,), _ = call_args[0]
        assert len(sent_message["jobs"]) == 3

        job_1_fetch = sent_message["jobs"][0]
        assert job_1_fetch["job_type"] == "FETCH_INVENTORY"
        assert job_1_fetch["item"]["uuid"] == "3ebae2d5-2f27-4150-abee-12e62511dbe5"

        job_2_fetch = sent_message["jobs"][1]
        assert job_2_fetch["job_type"] == "FETCH_INVENTORY"
        assert job_2_fetch["item"]["uuid"] == "4a6f4a2a-610c-436f-96fa-230597d59815"
        assert job_2_fetch["future_uuid"] is not None

        job_3_store = sent_message["jobs"][2]
        assert job_3_store["job_type"] == "STORE_INVENTORY"
        assert job_3_store["item"]["uuid"] == "3ebae2d5-2f27-4150-abee-12e62511dbe5"
        assert job_3_store["destination"]["uuid"] == job_2_fetch["future_uuid"]


@pytest.mark.asyncio
async def test_fetch_designated() -> None:
    async with TestRabbitBroker(broker) as br:
        message = [
            JobRequest(
                job_type="INT1",
                vendor="NLS",
            )
        ]
        await br.publish(message=message, queue="batch/request")

        # Validate received message
        handler_mock = batch_request_handler.mock
        handler_mock.assert_called_with([job.model_dump() for job in message])

        # Validate sent message
        call_args = mock_robot_batch_request_handler.mock.call_args_list
        assert len(call_args) == 1
        (sent_message,), _ = call_args[0]
        assert len(sent_message["jobs"]) == 1
        job = sent_message["jobs"][0]
        assert job["job_type"] == "FETCH_DESIGNATED"
        assert job["item"]["uuid"] == "5d62cadd-764a-4bb7-9839-739211ae1863"
        assert job["item"]["meta"]["item_type"] == "conveyor"


@pytest.mark.asyncio
async def test_store_inventory() -> None:
    async with TestRabbitBroker(broker) as br:
        message = [
            JobRequest(
                job_type="STORE_INVENTORY",
                vendor="RUBIC",
                uid="00100897774118155667",
                destination_uuid="aa451fb0-50fe-4d45-896b-776d80d07c51",
            )
        ]
        await br.publish(message=message, queue="batch/request")

        # Validate received message
        handler_mock = batch_request_handler.mock
        handler_mock.assert_called_with([job.model_dump() for job in message])

        # Validate sent message
        call_args = mock_robot_batch_request_handler.mock.call_args_list
        assert len(call_args) == 1
        (sent_message,), _ = call_args[0]
        assert len(sent_message["jobs"]) == 1
        job = sent_message["jobs"][0]
        assert job["job_type"] == "STORE_INVENTORY"
        assert job["item"]["uuid"] == "c6b452d3-7388-4716-a261-b1a0b6ec9268"
        assert job["destination"]["uuid"] == "aa451fb0-50fe-4d45-896b-776d80d07c51"


@pytest.mark.asyncio
async def test_store_designated() -> None:
    async with TestRabbitBroker(broker) as br:
        message = [
            JobRequest(
                job_type="INT2",
                vendor="NLS",
                uid="00100897774117552794",
            )
        ]
        await br.publish(message=message, queue="batch/request")

        # Validate received message
        handler_mock = batch_request_handler.mock
        handler_mock.assert_called_with([job.model_dump() for job in message])

        # Validate sent message
        call_args = mock_robot_batch_request_handler.mock.call_args_list
        assert len(call_args) == 1
        (sent_message,), _ = call_args[0]
        assert len(sent_message["jobs"]) == 1
        job = sent_message["jobs"][0]
        assert job["job_type"] == "STORE_DESIGNATED"
        assert job["item"]["uuid"] == "c4440f6a-7638-4872-91a2-7be10db915aa"
        assert job["destination"]["uuid"] == "5537a696-6a91-4f66-ba54-6fc472aa9328"
        assert job["destination"]["meta"]["item_type"] == "conveyor"
