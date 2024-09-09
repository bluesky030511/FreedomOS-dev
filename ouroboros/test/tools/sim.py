# Copyright 2024 The Rubic. All Rights Reserved.

import asyncio
import random
import uuid
from unittest.mock import patch

import matplotlib.pyplot as plt
import numpy as np
from faststream.annotations import Logger
from faststream.rabbit import TestRabbitBroker
from matplotlib.patches import Rectangle

from src.models import (
    Header,
    Item,
    ItemAbsolute,
    ItemMeta,
    ItemRelative,
    ItemUpdate,
    JobRequest,
    RobotBatchRequest,
    RobotBatchResponse,
    RobotJob,
    Timestamp,
    Vector3,
)
from src.models.db import Barcode, BarcodeAbsolute, BarcodeMeta, BarcodeRelative
from src.utils import validate_many_docs
from test.mock_database import MOCK_CLIENT

with (
    patch("azure.keyvault.secrets.SecretClient"),
    patch("azure.storage.blob.BlobServiceClient"),
    patch("pymongo.MongoClient", return_value=MOCK_CLIENT),
    patch("config.settings.AMQP_CONN_STR", new=""),
):
    from server import broker
    from src.routers import batch_router, inventory_router, robot_router

VALID_BARCODES = {"Code 128", "GS1-128"}


class SimInventory:
    def __init__(self, side: str, aisle_index: int):
        self.side = side
        self.aisle_index = aisle_index
        items = MOCK_CLIENT["Orbit"]["inventory_items"].find(
            {
                "relative.side": side,
                "meta.aisle_index": aisle_index,
            }
        )

        self.items = validate_many_docs(items, Item)
        self.boxes = {
            item.uuid: item
            for item in self.items
            if item.meta.item_type == "box" and self.has_barcode(item)
        }

    @staticmethod
    def has_barcode(item: Item) -> bool:
        for barcode in item.barcodes:
            if barcode.meta.barcode_type in VALID_BARCODES:
                return True
        return False

    def is_relevant_item(self, item: Item) -> bool:
        return (
            item.meta.location == "inventory"
            and item.relative.side == self.side
            and item.meta.aisle_index == self.aisle_index
        )

    def choose_item(self) -> Item:
        uuid = random.choice(list(self.boxes.keys()))
        item = self.boxes[uuid]
        del self.boxes[uuid]
        return item


class SimRobot:
    def __init__(self, inventory: SimInventory):
        self.backpack: dict[str, Item] = {}
        self.inventory = inventory

    def choose_item(self) -> Item:
        uuid = random.choice(list(self.backpack.keys()))
        return self.backpack[uuid]

    def handle_request(self, request: RobotBatchRequest) -> RobotBatchResponse:
        completed_jobs = []

        for job in request.jobs:
            completed_job = self.complete_job(job)
            completed_jobs.append(completed_job)

        return RobotBatchResponse(
            batch_id=request.batch_id,
            jobs=completed_jobs,
            success=True,
            error_code=0,
            error_message="",
        )

    def complete_job(self, job: RobotJob) -> RobotJob:
        match job.job_type:
            case "FETCH_INVENTORY":
                return self.fetch_inventory(job)
            case "STORE_INVENTORY":
                return self.store_inventory(job)
            case "FETCH_DESIGNATED":
                return self.fetch_designated(job)
            case "STORE_DESIGNATED":
                return self.store_designated(job)

    def fetch_inventory(self, job: RobotJob) -> RobotJob:
        self.backpack[job.item.uuid] = job.item
        job.success = True
        return job

    def store_inventory(self, job: RobotJob) -> RobotJob:
        self.inventory.boxes[job.item.uuid] = job.item
        del self.backpack[job.item.uuid]
        job.success = True
        job.item.absolute = job.destination.absolute
        job.item.meta.aisle_index = job.destination.meta.aisle_index
        return job

    def fetch_designated(self, job: RobotJob) -> RobotJob:
        rng = np.random.default_rng()
        dims = rng.normal(loc=0.4, scale=0.1, size=3)
        dims = np.clip(dims, 0.15, 0.60)
        x, y, z = dims
        if y > x:
            x, y = y, x
        barcode = Barcode(
            meta=BarcodeMeta(barcode_type="Code 128", data=str(uuid.uuid4())),
            absolute=BarcodeAbsolute(position=Vector3(x=0, y=0, z=0)),
            relative=BarcodeRelative(
                header=Header(
                    stamp=Timestamp(sec=0, nanosec=0), frame_id="parent_item"
                ),
                position=Vector3(x=0, y=0, z=0),
                dimension=Vector3(x=0.1, y=0.05, z=0),
                side="left",
            ),
        )
        item = Item(
            barcodes=[barcode],
            meta=ItemMeta(item_type="box"),
            absolute=ItemAbsolute(position=Vector3(x=0, y=0, z=0)),
            relative=ItemRelative(dimension=Vector3(x=x, y=y, z=z), side="left"),
            primary_barcode=barcode,
        )
        self.backpack[item.uuid] = item
        job.item = item
        job.success = True
        return job

    def store_designated(self, job: RobotJob) -> RobotJob:
        del self.backpack[job.item.uuid]
        job.success = True
        return job


class Simulator:
    def __init__(self, side: str, aisle_index: int):
        self.rectangles: dict[str, Rectangle] = {}
        self.inventory = SimInventory(side, aisle_index)
        self.robot = SimRobot(self.inventory)

        @inventory_router.subscriber("updates")
        async def update_visualization(body: list[ItemUpdate], logger: Logger) -> None:  # noqa: ARG001, RUF029
            self.update_visualization(body)

        @robot_router.subscriber("batch_request")
        @batch_router.publisher("response")
        async def mock_robot_batch_request_handler(  # noqa: RUF029
            body: RobotBatchRequest,
            logger: Logger,  # noqa: ARG001
        ) -> RobotBatchResponse:
            return self.robot.handle_request(body)

        broker.include_router(batch_router)
        broker.include_router(inventory_router)
        broker.include_router(robot_router)

    def init_visualization(self) -> None:
        self.fig, self.ax = plt.subplots()
        xs, ys = [], []
        for item in self.inventory.items:
            rect = self.create_rectangle(item)
            if rect is None:
                continue

            self.ax.add_patch(rect)
            xs.append(item.absolute.position.x)
            ys.append(item.absolute.position.y)

            self.rectangles[item.uuid] = rect

        self.ax.set(
            xlim=(min(xs) - 0.5, max(xs) + 0.5), ylim=(min(ys) - 0.5, max(ys) + 0.5)
        )
        self.ax.set_aspect("equal", adjustable="box")
        self.fig.set_figwidth(15)
        plt.show(block=False)

    def update_visualization(self, updates: list[ItemUpdate]) -> None:
        for rect in self.rectangles.values():
            rect.set_facecolor("white")

        for update in updates:
            match update.change:
                case "DELETED":
                    if update.item.uuid in self.rectangles:
                        self.rectangles[update.item.uuid].remove()
                        del self.rectangles[update.item.uuid]
                case "CREATED":
                    if self.inventory.is_relevant_item(update.item):
                        rect = self.add_new_rectangle(update.item)
                        rect.set_facecolor("purple")
                case "UPDATED":
                    self.update_item(update.item)
                case _:
                    raise ValueError

        self.fig.canvas.draw()

    def update_item(self, item: Item) -> None:
        if self.inventory.is_relevant_item(item):
            if item.uuid not in self.rectangles:
                rect = self.add_new_rectangle(item)
                rect.set_facecolor("magenta")
            else:
                rect = self.rectangles[item.uuid]
                rect.set_xy(
                    (
                        item.absolute.position.x - item.relative.dimension.x / 2,
                        item.absolute.position.y,
                    )
                )
                rect.set_visible(True)
                rect.set_facecolor("pink")
        elif item.uuid in self.rectangles:
            self.rectangles[item.uuid].set_visible(False)

    def add_new_rectangle(self, item: Item) -> Rectangle:
        rect = self.create_rectangle(item)
        self.ax.add_patch(rect)
        self.rectangles[item.uuid] = rect
        return rect

    def create_rectangle(self, item: Item) -> Rectangle:
        match item.meta.item_type:
            case "empty":
                color = "blue"
            case "box" if self.inventory.has_barcode(item):
                color = "green"
            case "box":
                color = "red"
            case _:
                return None

        width = item.relative.dimension.x
        height = item.relative.dimension.y
        x = item.absolute.position.x
        y = item.absolute.position.y

        return Rectangle(
            (x - width / 2, y),
            width,
            height,
            linewidth=1,
            edgecolor=color,
            facecolor="none",
        )

    @staticmethod
    def choose_barcode(item: Item) -> str:
        for barcode in item.barcodes:
            if barcode.meta.barcode_type in VALID_BARCODES:
                return barcode.meta.data
        raise ValueError("No valid barcode")

    def show_selected(self, selected: list[str]) -> None:
        for item_uuid in selected:
            self.rectangles[item_uuid].set_facecolor("green")
        self.fig.canvas.draw()

    @staticmethod
    def fetch_designated() -> list[JobRequest]:
        return [JobRequest(job_type="INT1", vendor="NLS")]

    def fetch_inventory(self) -> list[JobRequest]:
        item = self.inventory.choose_item()
        self.show_selected([item.uuid])
        input("Continue >")
        return [
            JobRequest(
                job_type="FETCH_INVENTORY",
                vendor="RUBIC",
                uid=self.choose_barcode(item),
            )
        ]

    def store_inventory(self) -> list[JobRequest]:
        item = self.robot.choose_item()
        return [
            JobRequest(
                job_type="STORE_INVENTORY",
                vendor="RUBIC",
                uid=self.choose_barcode(item),
            )
        ]

    def get_message(self) -> list[JobRequest]:
        request = input("Next request? >")
        if not request:
            request = self.prev_request
        self.prev_request = request

        match request:
            case "f":
                return self.fetch_inventory()
            case "d":
                return self.fetch_designated()
            case "s":
                return self.store_inventory()

    async def run(self) -> None:
        self.init_visualization()

        async with TestRabbitBroker(broker) as br:
            while True:
                await br.publish(message=self.get_message(), queue="batch/request")


if __name__ == "__main__":
    sim = Simulator("left", 35)
    asyncio.run(sim.run())
