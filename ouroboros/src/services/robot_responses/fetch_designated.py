# Copyright 2024 The Rubic. All Rights Reserved.

"""Implements concrete fetch designated response processing."""

import uuid

from loguru import logger

from db.mongodb import barcode_collection, inventory_items
from src.models import Barcode, ItemUpdate, RobotJob
from src.utils import validate_many_docs

from .base_robot_response import RobotResponseABC


class FetchDesignatedRobotResponse(RobotResponseABC):
    """Process fetch designated response."""

    job_type: str = "fetch"

    def update_inventory(self, job: RobotJob) -> None:
        """Update items in inventory."""
        item = job.item
        # Check if item exists
        if not item.uuid:
            item.uuid = str(uuid.uuid4())
            logger.info("Assigning item with uuid: {}", item.uuid)

        item.meta.location = "robot"
        item.meta.destination = None
        item.meta.available = False

        barcodes = item.barcodes
        valid_priority_barcodes = (
            "GS1-128",
            "Code 128",
        )
        priority_barcodes: list[Barcode] = list(
            filter(
                lambda x: x.meta.barcode_type in valid_priority_barcodes,
                barcodes,
            )
        )
        if not priority_barcodes:
            raise ValueError(
                "Conductor fetch designated callback received an item without "
                f"a barcode of types {valid_priority_barcodes}",
            )

        priority_barcodes_data = [x.meta.data for x in priority_barcodes]

        inventory_barcodes_doc = barcode_collection.find(
            {"barcode": {"$in": priority_barcodes_data}}
        )
        inventory_barcodes = validate_many_docs(inventory_barcodes_doc, Barcode)
        if not inventory_barcodes:
            # The barcode from the item is not in the inventory
            # So make the item
            item_uuid = item.uuid
            inventory_items.insert_one(item.model_dump())
            # insert all the barcodes
            for barcode in barcodes:
                barcode.item_uuid = item_uuid
                barcode_collection.insert_one(barcode.model_dump())

            logger.info("Created new item with uuid: {}", item.uuid)
            self.updates.append(ItemUpdate(change="UPDATED", item=item))
        else:
            # The barcode from the item is in the inventory
            matched_barcodes = [barcode.meta.data for barcode in inventory_barcodes]
            raise ValueError(
                "The item from designated fetch already exists in the inventory. "
                "Matched barcodes: %s",
                matched_barcodes,
            )
