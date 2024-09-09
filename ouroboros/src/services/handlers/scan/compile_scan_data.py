# Copyright 2024 The Rubic. All Rights Reserved.

"""CompileScanDataRequest handler."""

from faststream.rabbit.annotations import Logger
from loguru import logger

from db.mongodb import (
    barcode_collection,
    inventory_items,
    partial_barcode_collection,
    partial_item_collection,
)
from src.models import Barcode, CompileScanDataRequest, Item, PartialItem
from src.services.handlers import Handler
from src.services.model.barcode import BarcodeService
from src.services.model.item import ItemService
from src.services.model.partial_item import PartialItemService
from src.utils import validate_many_docs


class CompileScanData(Handler):
    """Compile scan request handler."""

    def __init__(self, request: CompileScanDataRequest):
        """Init compilation parameters."""
        self.request = request

        # These types are hardcoded. TODO: make this configurable
        self.to_compile_types = (
            ["empty", "box"] if request.item_type is None else [request.item_type]
        )
        self.to_compile_sides = (
            ["left", "right"] if request.side is None else [request.side]
        )
        self.to_compile_aisle_indexes = (
            (partial_item_collection.distinct("meta.aisle_index"))
            if request.aisle_index is None
            else [request.aisle_index]
        )

        if request.item_type is None:
            logger.info(
                "No item type specified, so compiling all types {}",
                self.to_compile_types,
            )
        if request.side is None:
            logger.info(
                "No side specified, so compiling all sides {}",
                self.to_compile_sides,
            )

    async def run(self, logger: Logger) -> None:
        """Handle user requests a scan data compilation."""
        try:
            items = self.compile_partial_items()
        except ValueError:
            logger.exception("Failed to compile scan. Unable to compile partial items.")
            return

        # Insert items into db
        item_docs = [
            Item.model_dump(item, exclude={"primary_barcode"}) for item in items
        ]
        insert_result = inventory_items.insert_many(item_docs)

        logger.info(
            "Inserted {} completed items into database", len(insert_result.inserted_ids)
        )

        # Insert combination into db
        for item in items:
            for barcode in item.barcodes:
                barcode_doc = barcode.model_dump()
                barcode_collection.insert_one(barcode_doc)

        logger.info("Inserted barcode-item combinations into database")

    def compile_partial_items(self) -> list[Item]:
        """Compile partial items."""
        if not self.request:
            raise ValueError("Request is not set. Cannot compile partial items.")

        if self.request.overwrite:
            logger.info(
                "Overwrite was set to TRUE."
                f"Deleting existing clusters for scan_id {self.request.scan_id}",
            )
            inventory_items.delete_many({"meta.item_type": {"$ne": "conveyor"}})

        all_new_completed_items: list[Item] = []
        for to_compile_aisle_index in self.to_compile_aisle_indexes:
            for to_compile_side in self.to_compile_sides:
                items: dict[str, list[Item]] = {}
                for to_compile_type in self.to_compile_types:
                    logger.info(
                        f"Compiling type {to_compile_type} "
                        f"for the {to_compile_side} side"
                    )
                    query = {
                        "meta.item_type": to_compile_type,
                        "meta.scan_id": self.request.scan_id,
                        "meta.aisle_index": to_compile_aisle_index,
                        "meta.confidence": {"$gte": self.request.confidence_threshold},
                        "relative.side": to_compile_side,
                        "absolute.dimension.x": {"$gte": 0.08},
                    }
                    partial_items_doc = partial_item_collection.find(
                        query
                        # Needs to be with aligned axis : TODO
                    ).sort([("absolute.position.x", 1)])

                    if not partial_items_doc:
                        logger.warning(
                            f"No partial items found for request "
                            f"{self.request.model_dump_json()} QUERY: "
                            f"{query}. [SKIPPING]"
                        )
                        continue

                    partial_items = validate_many_docs(partial_items_doc, PartialItem)

                    logger.info(
                        "Building complete items for {} items for request {}",
                        len(partial_items),
                        self.request.model_dump_json(),
                    )

                    _items = PartialItemService.merge(partial_items)
                    items[to_compile_type] = _items

                # If there are boxes, make sure we add the barcodes to the items
                if items.get("box"):
                    items["box"] = self.compile_partial_barcodes(
                        to_compile_side, to_compile_aisle_index, items["box"]
                    )

                for _items in items.values():
                    all_new_completed_items.extend(_items)

        logger.info("Built complete items. Inserting into database...")
        return all_new_completed_items

    def compile_partial_barcodes(
        self, side: str, aisle_index: int, items: list[Item]
    ) -> list[Item]:
        """Compile barcodes and updates the items."""
        if self.request.overwrite:
            logger.info(
                "Overwrite was set to TRUE. Deleting existing barcodes for scan_id {}",
                self.request.scan_id,
            )
            barcode_collection.delete_many({})

        all_new_barcodes: list[Barcode] = []
        query = {
            "meta.scan_id": self.request.scan_id,
            "meta.aisle_index": aisle_index,
            "relative.side": side,
        }
        partial_barcodes_doc = partial_barcode_collection.find(
            query
            # Needs to be with aligned axis : TODO
        ).sort([("absolute.position.x", 1)])
        if not partial_barcodes_doc:
            raise ValueError(
                f"No partial items found for request {self.request.model_dump_json()}"
            )
        barcodes = validate_many_docs(partial_barcodes_doc, Barcode)

        logger.info(
            "Clustering {} barcodes for the {} side",
            len(barcodes),
            side,
        )

        clustered_barcodes = BarcodeService.merge(barcodes)

        all_new_barcodes.extend(clustered_barcodes)

        items = ItemService.combine_barcodes(items, all_new_barcodes)
        # Recompute the barcode (relative) positions based on the item positions
        for item in items:
            for barcode in item.barcodes:
                barcode.relative.position.x = (
                    barcode.absolute.position.x - item.absolute.position.x
                )
                barcode.relative.position.y = (
                    barcode.absolute.position.y - item.absolute.position.y
                )
                barcode.relative.position.z = (
                    barcode.absolute.position.z - item.absolute.position.z
                )
                barcode.relative.header.frame_id = "parent_item"

        return items
