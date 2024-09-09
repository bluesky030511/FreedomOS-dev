# Copyright 2024 The Rubic. All Rights Reserved.

"""Implements concrete store designated response processing."""

from loguru import logger

from db.mongodb import barcode_collection, inventory_items
from src.models import ItemUpdate, RobotJob

from .base_robot_response import RobotResponseABC


class StoreDesignatedRobotResponse(RobotResponseABC):
    """Process store designated response."""

    job_type: str = "store"

    def update_inventory(self, job: RobotJob) -> None:
        """Update items in inventory."""
        item = job.item
        # Delete the item
        query = {"uuid": item.uuid}
        delete_result = inventory_items.delete_one(query)
        if delete_result.deleted_count == 0:
            raise ValueError(
                f'No item with uuid="{item.uuid}" found in inventory_items'
            )

        # Delete the barcodes
        barcode_collection.delete_many({"item_uuid": item.uuid})
        logger.info("Deleted item and associated barcodes with uuid: {}", item.uuid)
        self.updates.append(ItemUpdate(change="DELETED", item=item))
