# Copyright 2024 The Rubic. All Rights Reserved.

"""Implements concrete fetch inventory response processing."""

from loguru import logger

from db.mongodb import inventory_items
from src.models import (
    Item,
    ItemAbsolute,
    ItemMeta,
    ItemRelative,
    ItemUpdate,
    Rectangle,
    RobotJob,
    Vector2,
    Vector3,
)
from src.services.model.rectangle import RectangleService
from src.utils import validate_doc, validate_many_docs

from .base_robot_response import RobotResponseABC


class FetchInventoryRobotResponse(RobotResponseABC):
    """Process fetch inventory response."""

    job_type: str = "fetch"

    def update_inventory(self, job: RobotJob) -> None:
        """Update items in inventory.

        1. Move item to Robot
        2. Create empty in place of item
        """
        item = job.item
        # Need to update the target item
        uuid = item.uuid
        # We need to check that the box was not from inventory
        query = {
            "uuid": uuid,
            "meta.location": "inventory",
        }
        doc = inventory_items.find_one(query)
        if doc is None:
            raise ValueError(
                f'No item with uuid="{item.uuid}" and '
                'meta.location="inventory" found in inventory_items'
            )

        # if the item is from the conveyor, we use the one given by conductor.
        # else we update the one in the db
        item = validate_doc(doc, Item)
        item.meta.available = False
        item.meta.location = "robot"

        item_doc = item.model_dump()
        new_values = {"$set": item_doc}
        update_result = inventory_items.update_one(query, new_values, upsert=True)
        is_upserted = update_result.upserted_id is None
        logger.info(
            "Updated inventory item with uuid: {}. Upserted: {}", uuid, is_upserted
        )
        self.updates.append(ItemUpdate(change="UPDATED", item=item))

        empty_item = Item(
            meta=ItemMeta(
                item_type="empty",
                available=True,
                location="inventory",
                destination=None,
                aisle_index=item.meta.aisle_index,
                # stack is not needed since when we pick, the stack should be empty
            ),
            absolute=item.absolute,
            relative=item.relative,
        )
        if job.future_uuid:
            empty_item.uuid = job.future_uuid
        else:
            empty_item = self.merge_empty(empty_item)

        inventory_items.insert_one(empty_item.model_dump())
        logger.info("Created new empty item with uuid: {}", empty_item.uuid)
        self.updates.append(ItemUpdate(change="CREATED", item=empty_item))

        # Update all items that contains picked item as stack
        query = {"meta.stack": item.uuid}
        affected_items = inventory_items.find(query)
        affected_items = validate_many_docs(affected_items, Item)

        for affected_item in affected_items:
            # Remove item uuid from affected item stack
            affected_item.meta.stack.remove(item.uuid)
            # Update affected item
            affected_item_doc = affected_item.model_dump()
            inventory_items.update_one(
                {"uuid": affected_item.uuid}, {"$set": affected_item_doc}
            )
            logger.info("Updated meta stack for item with uuid {}", affected_item.uuid)
            self.updates.append(ItemUpdate(change="UPDATED", item=affected_item))

    def merge_empty(self, empty: Item, margin: float = 0.1) -> Item:
        """Try merge empty with nearby empties."""
        query = {
            "meta.aisle_index": empty.meta.aisle_index,
            "meta.location": "inventory",
            "relative.side": empty.relative.side,
            "absolute.position.x": {
                "$gt": empty.bounding_box.bottom_left.x - 2.0,
                "$lt": empty.bounding_box.top_right.x + 2.0,
            },
            "absolute.position.y": {
                "$gt": empty.absolute.position.y - 1.0,
                "$lt": empty.absolute.position.y + 1.0,
            },
        }
        nearby_items = inventory_items.find(query)
        nearby_items = validate_many_docs(nearby_items, Item)

        items_below = [
            item
            for item in nearby_items
            if abs(item.bounding_box.top_right.y - empty.absolute.position.y) < margin
            and item.bounding_box.top_right.x > empty.bounding_box.bottom_left.x
            and item.bounding_box.bottom_left.x < empty.bounding_box.top_right.x
            and item.meta.item_type == "box"
        ]

        if items_below:
            empty = self.expand_empty_on_item(empty, items_below, nearby_items)
        else:
            empty = self.expand_empty(empty, nearby_items)

        return self.merge_empty_above(empty, nearby_items)

    def merge_empty_above(
        self, empty: Item, nearby_items: list[Item], margin: float = 0.1
    ) -> Item:
        """Merge empty with the empty above it."""
        items_above = [
            item
            for item in nearby_items
            if abs(item.absolute.position.y - empty.bounding_box.top_right.y) < margin
            and item.bounding_box.top_right.x > empty.bounding_box.bottom_left.x
            and item.bounding_box.bottom_left.x < empty.bounding_box.top_right.x
            and item.meta.item_type == "empty"
        ]

        if not items_above:
            return empty

        above = max(items_above, key=lambda x: overlap(x, empty))
        additional_height = (
            above.bounding_box.top_right.y - empty.bounding_box.top_right.y
        )
        empty.relative.dimension.y += additional_height

        inventory_items.delete_one({"uuid": above.uuid, "meta.item_type": "empty"})
        self.updates.append(ItemUpdate(change="DELETED", item=above))

        return empty

    @classmethod
    def expand_empty_on_item(
        cls, empty: Item, items_below: list[Item], nearby_items: list[Item]
    ) -> Item:
        """Maximize empty on item."""
        below = max(items_below, key=lambda x: overlap(x, empty))

        left_limit = below.bounding_box.bottom_left.x
        left_edge = cls.get_left_edge(empty, nearby_items)
        if left_edge is not None and left_edge.meta.item_type == "box":
            left_limit = max(
                left_edge.bounding_box.top_right.x, below.bounding_box.bottom_left.x
            )

        right_limit = below.bounding_box.top_right.x
        right_edge = cls.get_right_edge(empty, nearby_items)
        if right_edge is not None and right_edge.meta.item_type == "box":
            right_limit = min(
                right_edge.bounding_box.bottom_left.x, below.bounding_box.top_right.x
            )

        return cls.construct_empty(empty, left_limit, right_limit)

    def expand_empty(self, empty: Item, nearby_items: list[Item]) -> Item:
        """Maximize empty."""
        left_edge = self.get_left_edge(empty, nearby_items)
        if left_edge is not None:
            if left_edge.meta.item_type == "box":
                empty = self.construct_empty(
                    empty,
                    left_edge.bounding_box.top_right.x,
                    empty.bounding_box.top_right.x,
                )
            elif left_edge.meta.item_type == "empty":
                empty = self.merge_empty_side(empty, left_edge)

        right_edge = self.get_right_edge(empty, nearby_items)
        if right_edge is not None:
            if right_edge.meta.item_type == "box":
                empty = self.construct_empty(
                    empty,
                    empty.bounding_box.bottom_left.x,
                    right_edge.bounding_box.bottom_left.x,
                )
            elif right_edge.meta.item_type == "empty":
                empty = self.merge_empty_side(empty, right_edge)

        return empty

    def merge_empty_side(self, empty: Item, side_empty: Item) -> Item:
        """Merge empty with its neighbor."""
        left_limit = min(
            empty.bounding_box.bottom_left.x, side_empty.bounding_box.bottom_left.x
        )
        right_limit = max(
            empty.bounding_box.top_right.x, side_empty.bounding_box.top_right.x
        )
        empty = self.construct_empty(empty, left_limit, right_limit)

        inventory_items.delete_one({"uuid": side_empty.uuid, "meta.item_type": "empty"})
        self.updates.append(ItemUpdate(change="DELETED", item=side_empty))

        return empty

    @staticmethod
    def get_left_edge(
        empty: Item, nearby_items: list[Item], margin: float = 0.1
    ) -> Item | None:
        """Get left limit of empty."""
        left = [
            item
            for item in nearby_items
            if abs(item.absolute.position.y - empty.absolute.position.y) < margin
            and abs(item.bounding_box.top_right.x - empty.bounding_box.bottom_left.x)
            < margin
        ]

        if left:
            return left[0]
        return None

    @staticmethod
    def get_right_edge(
        empty: Item, nearby_items: list[Item], margin: float = 0.1
    ) -> Item | None:
        """Get right limit of empty."""
        right = [
            item
            for item in nearby_items
            if abs(item.absolute.position.y - empty.absolute.position.y) < margin
            and abs(item.bounding_box.bottom_left.x - empty.bounding_box.top_right.x)
            < margin
        ]

        if right:
            return right[0]
        return None

    @staticmethod
    def construct_empty(empty: Item, left_limit: float, right_limit: float) -> Item:
        """Construct an expandend empty item."""
        bounding_box = Rectangle(
            bottom_left=Vector2(x=left_limit, y=empty.absolute.position.y),
            top_right=Vector2(x=right_limit, y=empty.bounding_box.top_right.y),
        )
        dimension = Vector3(
            x=abs(left_limit - right_limit),
            y=abs(empty.absolute.position.y - empty.bounding_box.top_right.y),
            z=0,
        )
        item_relative = ItemRelative(dimension=dimension, side=empty.relative.side)

        bottom_center_point = RectangleService.get_bottom_center_point(bounding_box)
        item_absolute = ItemAbsolute(
            position=Vector3(
                x=bottom_center_point.x,
                y=bottom_center_point.y,
                z=empty.absolute.position.z,
            ),
            aligned_axis=empty.absolute.aligned_axis,
        )
        return Item(meta=empty.meta, absolute=item_absolute, relative=item_relative)


def overlap(item_a: Item, item_b: Item) -> float:
    """Calculate horizontal overlap between items."""
    left = max(item_a.bounding_box.bottom_left.x, item_b.bounding_box.bottom_left.x)
    right = min(item_a.bounding_box.top_right.x, item_b.bounding_box.top_right.x)
    return right - left
