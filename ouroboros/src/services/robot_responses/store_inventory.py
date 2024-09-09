# Copyright 2024 The Rubic. All Rights Reserved.

"""Implements concrete store inventory response processing."""

from loguru import logger

from db.mongodb import inventory_items
from src.models import Item, ItemAbsolute, ItemRelative, ItemUpdate, RobotJob, Vector3
from src.services.model.item import ItemService
from src.services.model.rectangle import RectangleService
from src.utils import validate_many_docs

from .base_robot_response import RobotResponseABC


class StoreInventoryRobotResponse(RobotResponseABC):
    """Process store inventory response."""

    job_type: str = "store"

    def update_inventory(self, job: RobotJob) -> None:
        """Update items in inventory.

        1. Update the stored item.
        2. Delete the empty it was stored in.
        """
        item = job.item

        if job.destination is None:
            raise ValueError("Received store inventory job without destination")

        destination_doc = inventory_items.find_one({"uuid": job.destination.uuid})
        destination = Item.model_validate(destination_doc)

        query = {"uuid": item.uuid}
        item.meta.item_type = "box"
        item.meta.available = True
        item.meta.location = "inventory"
        item.meta.destination = None

        # Update the barcodes
        for barcode in item.barcodes:
            barcode.meta.aisle_index = item.meta.aisle_index

        update = {
            "$set": {
                "meta": item.meta.model_dump(),
                "absolute": item.absolute.model_dump(),
                "relative": item.relative.model_dump(),
                "barcodes": [barcode.model_dump() for barcode in item.barcodes],
            },
        }
        inventory_items.find_one_and_update(query, update, upsert=True)
        logger.info("Updated inventory item with uuid: {}", item.uuid)
        self.updates.append(ItemUpdate(change="UPDATED", item=item))

        # Slice the destination item
        new_rectangles = RectangleService.slice_rectangle(
            destination.bounding_box, item.bounding_box
        )
        for new_rectangle in new_rectangles:
            new_rect_pos_vec2 = RectangleService.get_bottom_center_point(new_rectangle)

            new_relative_dimension = Vector3.model_validate(
                {
                    "x": new_rectangle.width,
                    "y": new_rectangle.height,
                    "z": destination.relative.dimension.z,
                }
            )
            new_absolute_position = Vector3.model_validate(
                {
                    destination.absolute.aligned_axis: new_rect_pos_vec2.x,
                    "y": new_rect_pos_vec2.y,
                    "z"
                    if destination.absolute.aligned_axis == "x"
                    else "x": destination.absolute.position.z,
                }
            )
            new_empty = Item(
                meta=destination.meta,
                relative=ItemRelative(
                    header=destination.relative.header,
                    dimension=new_relative_dimension,
                    side=destination.relative.side,
                ),
                absolute=ItemAbsolute(
                    depth_index=destination.absolute.depth_index,
                    stack_index=destination.absolute.stack_index,
                    aligned_axis=destination.absolute.aligned_axis,
                    position=new_absolute_position,
                    waypoint=destination.absolute.waypoint,
                ),
            )
            inventory_items.insert_one(new_empty.model_dump())
            self.updates.append(ItemUpdate(change="CREATED", item=new_empty))

        inventory_items.delete_one(
            {"uuid": destination.uuid, "meta.item_type": "empty"}
        )
        self.updates.append(ItemUpdate(change="DELETED", item=destination))

        # Query for nearby boxes underneath
        item_position = item.absolute.position
        query = {
            "relative.side": destination.relative.side,  # item side cant be trusted
            "meta.location": "inventory",
            "meta.available": True,
            "meta.item_type": "box",
            "meta.aisle_index": item.meta.aisle_index,
            "absolute.position.x": {
                "$gte": item_position.x - 1,
                "$lte": item_position.x + 1,
            },
            "absolute.position.y": {
                "$gte": item_position.y - 1,
                "$lte": item_position.y + 1,
            },
        }
        nearby_boxes_doc = inventory_items.find(query)
        nearby_boxes = validate_many_docs(nearby_boxes_doc, Item)
        item_stack = ItemService.generate_item_stack(nearby_boxes)

        for nearby_box in nearby_boxes:
            new_stacks = item_stack.get(nearby_box.uuid)
            if not new_stacks:
                continue

            if nearby_box.meta.stack:
                nearby_box.meta.stack.extend(new_stacks)
            else:
                nearby_box.meta.stack = new_stacks

            # De-duplicate the stack
            nearby_box.meta.stack = list(set(nearby_box.meta.stack))

            # Update the inventory
            inventory_items.update_one(
                {"uuid": nearby_box.uuid},
                {"$set": {"meta.stack": nearby_box.meta.stack}},
            )
            self.updates.append(ItemUpdate(change="UPDATED", item=nearby_box))

        logger.info(
            "Deleted destination item of type {} with uuid: {}",
            destination.meta.item_type,
            destination.uuid,
        )
