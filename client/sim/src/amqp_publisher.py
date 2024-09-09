# Copyright 2024 The Rubic. All Rights Reserved.

from __future__ import annotations

import json
import time

import pika
import pika.exceptions

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASSWORD = "guest"


class AMQPPublisher:
    def __init__(self):
        self.wait_for_rabbitmq()
        self.reset_connection()

    def wait_for_rabbitmq(self) -> None:
        while True:
            try:
                self._connection = self._create_connection()
                self._connection.close()
                break
            except pika.exceptions.AMQPConnectionError:
                print("RabbitMQ is not available yet. Retrying...")
                time.sleep(1)

    def reset_connection(self) -> None:
        self._connection = self._create_connection()
        self._channel = self._connection.channel()
        self._channel.confirm_delivery()

    def _create_connection(self) -> pika.BlockingConnection:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection_parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )
        return pika.BlockingConnection(connection_parameters)

    def add_exchange(self, amqp_endpoint: str) -> None:
        self._channel.exchange_declare(
            exchange=amqp_endpoint,
            exchange_type="fanout",
        )

    def add_queue(self, amqp_endpoint: str) -> None:
        self._channel.queue_declare(queue=amqp_endpoint)

    def publish(self, data: dict, amqp_endpoint: str) -> None:
        data_str = json.dumps(data)
        self._channel.basic_publish(
            exchange=amqp_endpoint,
            routing_key="",
            body=data_str,
        )

    def publish_queue(self, data: dict, amqp_endpoint: str) -> None:
        data_str = json.dumps(data)
        self._channel.basic_publish(
            exchange="",
            routing_key=amqp_endpoint,
            body=data_str,
        )
