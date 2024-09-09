# Copyright 2024 The Rubic. All Rights Reserved.

"""Module to implement factory pattern for producer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from db.mongodb import barcode_collection, inventory_items
from src.models import Barcode, Item, ItemMeta
from src.utils import validate_many_docs

if TYPE_CHECKING:
    from src.models import JobRequest, JobType, RobotJob


class RobotJobBuilderABC(ABC):
    """Abstract class for robot requests."""

    def __init__(
        self, request: JobRequest, job_type: JobType, fetched_items: dict[str, str]
    ):
        """Initialize the RobotRequest class."""
        self.request = request
        self.job_type = job_type
        self.fetched_items = fetched_items

    @abstractmethod
    def build_jobs(self) -> list[RobotJob]:
        """Abstract method to be implemented by concrete builders."""

    @staticmethod
    def get_item_from_barcode(barcode_uid: str | None) -> Item:
        """Get the item from barcode."""
        if barcode_uid is None:
            raise ValueError("Barcode uid not specified")

        query = {"meta.data": barcode_uid}
        barcode_docs = barcode_collection.find(query)
        barcodes = validate_many_docs(barcode_docs, Barcode)
        if not barcodes:
            raise ValueError(
                f"Failed to find barcode with uid {barcode_uid} from "
                "barcode collection. Either the barcode is invalid or doesn't exist"
            )
        if len(barcodes) > 1:
            raise ValueError(
                f"Multiple barcodes found for uid {barcode_uid}. This is not expected"
            )
        barcode = barcodes[0]

        item_uuid = barcode.item_uuid
        item_doc = inventory_items.find_one({"uuid": item_uuid})
        if item_doc is None:
            raise ValueError(
                f"Failed to find item with uid {barcode_uid} from inventory collection."
                " Either the item is invalid or doesn't exist"
            )
        item = Item.model_validate(item_doc)
        item.primary_barcode = barcode

        return item

    @staticmethod
    def get_item(uuid: str) -> Item:
        """Get the item from uuid."""
        item_doc = inventory_items.find_one({"uuid": uuid})
        if item_doc is None:
            raise ValueError(
                f"Failed to find item with uuid {uuid} "
                "from inventory collection. "
                "Either the item is invalid or doesn't exist"
            )
        return Item.model_validate(item_doc)

    @staticmethod
    def get_primary_barcode(item_uuid: str) -> Barcode:
        """Find primary barcode for item with specified uuid."""
        primary_barcode_doc = barcode_collection.find_one(
            {
                "item_uuid": item_uuid,
                "$or": [
                    {"meta.barcode_type": "GS1-128"},
                    {"meta.barcode_type": "Code 128"},
                ],
            }
        )

        if primary_barcode_doc is None:
            raise ValueError(
                "Failed to find a valid primary barcode for item "
                f"with uuid {item_uuid}"
            )

        return Barcode.model_validate(primary_barcode_doc)

    @staticmethod
    def create_future_empty(future_uuid: str, item: Item) -> Item:
        """Create a future hypothetical empty, potentially created by a fetch."""
        return Item(
            meta=ItemMeta(
                item_type="empty",
                location="inventory",
                available=True,
                aisle_index=item.meta.aisle_index,
            ),
            absolute=item.absolute,
            relative=item.relative,
            uuid=future_uuid,
        )
