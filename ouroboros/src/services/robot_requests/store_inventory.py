# Copyright 2024 The Rubic. All Rights Reserved.

"""Module to implement concrete conductor store request."""

from __future__ import annotations

from typing import Any, Literal

from db.mongodb import inventory_items
from src.models import (
    Item,
    ItemAbsolute,
    ItemRelative,
    Rectangle,
    RobotJob,
    Vector2,
    Vector3,
)
from src.services.model.rectangle import RectangleService
from src.utils import validate_many_docs

from .base_robot_job_builder import RobotJobBuilderABC


class StoreInventoryRobotJobBuilder(RobotJobBuilderABC):
    """Implements RobotJobBuilder for store request jobs."""

    def build_jobs(self) -> list[RobotJob]:
        """Build store inventory jobs."""
        target_item = self.get_item_from_barcode(self.request.uid)
        # Check if the target_item is on robot
        is_valid = (
            target_item.meta.location == "robot"
            and target_item.meta.destination is None
            and not target_item.meta.available
        ) or target_item.primary_barcode.meta.data in self.fetched_items
        if not is_valid:
            raise ValueError(
                f"Item with uid {self.request.uid} is not available or not in robot"
            )

        if self.request.destination_uuid is None:
            destination_item = self.find_empty(target_item)
        elif self.fetched_items.get(self.request.destination_uuid) is not None:
            future_uuid = self.fetched_items[self.request.destination_uuid]
            item = self.get_item_from_barcode(self.request.destination_uuid)
            destination_item = self.create_future_empty(future_uuid, item)
        else:
            destination_item = self.get_item(self.request.destination_uuid)
        # Check if the destination item is valid
        is_valid = (
            destination_item.meta.available
            and destination_item.meta.location == "inventory"
            and destination_item.meta.destination is None
            and destination_item.meta.item_type == "empty"
        )
        if not is_valid:
            raise ValueError(
                f"Destination item with uuid {destination_item.uuid} is "
                "not available or not in inventory or not empty"
            )
        return [
            RobotJob(
                job_type="STORE_INVENTORY",
                item=target_item,
                destination=destination_item,
            )
        ]

    def find_empty(self, target_item: Item, store_margin: float = 0.03) -> Item:
        """Method to find best fit empty in inventory."""
        item_width = target_item.relative.dimension.x + 2 * store_margin
        item_height = target_item.relative.dimension.y + store_margin
        pipeline: list[dict[str, Any]] = [
            {
                "$match": {
                    "relative.dimension.x": {"$gt": item_width},
                    "relative.dimension.y": {"$gt": item_height},
                    "relative.side": target_item.relative.side,
                    "meta.item_type": "empty",
                }
            },
            {
                "$addFields": {
                    "area": {
                        "$multiply": ["$relative.dimension.x", "$relative.dimension.y"]
                    }
                }
            },
            {"$sort": {"area": 1}},
            {"$limit": 1},
        ]
        empty_items_doc = inventory_items.aggregate(pipeline)
        empty_items = validate_many_docs(empty_items_doc, Item)
        if not empty_items:
            raise ValueError("No empty items found in inventory")

        return self.build_positioned_empty(target_item, empty_items[0], store_margin)

    def build_positioned_empty(
        self, target_item: Item, empty: Item, store_margin: float
    ) -> Item:
        """Modify empty to target specific position."""
        side = self.choose_side_in_empty(empty)

        if side is None:
            return empty

        if side == "left":
            left_limit = empty.bounding_box.bottom_left.x
            right_limit = (
                empty.bounding_box.bottom_left.x
                + target_item.relative.dimension.x
                + 2 * store_margin
            )
        else:
            left_limit = (
                empty.bounding_box.top_right.x
                - target_item.relative.dimension.x
                - 2 * store_margin
            )
            right_limit = empty.bounding_box.top_right.x

        return self.construct_empty(empty, left_limit, right_limit)

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
        return Item(
            meta=empty.meta,
            absolute=item_absolute,
            relative=item_relative,
            uuid=empty.uuid,
        )

    def choose_side_in_empty(
        self, empty: Item, alignment_margin: float = 0.1
    ) -> Literal["left", "right"] | None:
        """Choose target side in empty."""
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
            if abs(item.bounding_box.top_right.y - empty.absolute.position.y)
            < alignment_margin
            and item.bounding_box.top_right.x > empty.bounding_box.bottom_left.x
            and item.bounding_box.bottom_left.x < empty.bounding_box.top_right.x
            and item.meta.item_type == "box"
        ]

        if items_below:
            # If stacked store then just store in middle
            return None

        return self.find_nearest_box(empty, nearby_items)

    def find_nearest_box(
        self, empty: Item, nearby_items: list[Item]
    ) -> Literal["left", "right"] | None:
        """Find nearest_box."""
        left_edge = self.get_left_edge(empty, nearby_items)
        right_edge = self.get_right_edge(empty, nearby_items)

        if left_edge is not None and left_edge.meta.item_type == "box":
            left_distance = abs(
                empty.bounding_box.bottom_left.x - left_edge.bounding_box.top_right.x
            )
        else:
            left_distance = float("inf")

        if right_edge is not None and right_edge.meta.item_type == "box":
            right_distance = abs(
                empty.bounding_box.top_right.x - right_edge.bounding_box.bottom_left.x
            )
        else:
            right_distance = float("inf")

        if left_distance == right_distance == float("inf"):
            return None

        if left_distance < right_distance:
            return "left"

        return "right"

    @staticmethod
    def get_left_edge(
        empty: Item, nearby_items: list[Item], alignment_margin: float = 0.1
    ) -> Item | None:
        """Get left limit of empty."""
        left = [
            item
            for item in nearby_items
            if abs(item.absolute.position.y - empty.absolute.position.y)
            < alignment_margin
            and abs(item.bounding_box.top_right.x - empty.bounding_box.bottom_left.x)
            < alignment_margin
        ]

        if left:
            return left[0]
        return None

    @staticmethod
    def get_right_edge(
        empty: Item, nearby_items: list[Item], alignment_margin: float = 0.1
    ) -> Item | None:
        """Get right limit of empty."""
        right = [
            item
            for item in nearby_items
            if abs(item.absolute.position.y - empty.absolute.position.y)
            < alignment_margin
            and abs(item.bounding_box.bottom_left.x - empty.bounding_box.top_right.x)
            < alignment_margin
        ]

        if right:
            return right[0]
        return None


def overlap(item_a: Item, item_b: Item) -> float:
    """Calculate horizontal overlap between items."""
    left = max(item_a.bounding_box.bottom_left.x, item_b.bounding_box.bottom_left.x)
    right = min(item_a.bounding_box.top_right.x, item_b.bounding_box.top_right.x)
    return right - left
