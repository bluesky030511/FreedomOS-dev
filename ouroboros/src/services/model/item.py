# Copyright 2024 The Rubic. All Rights Reserved.

"""Concrete item."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import numpy as np

from src.models import (
    Barcode,
    Item,
    ItemAbsolute,
    ItemMeta,
    ItemRelative,
    Rectangle,
    Vector2,
    Vector3,
)
from src.services.model.rectangle import RectangleService

if TYPE_CHECKING:
    from src.models import PartialItem


class ItemService:
    """Item model."""

    @classmethod
    def from_partial_items(cls, partial_items: list[PartialItem]) -> Item:
        """Method to generate information for item.

        We have the following information:
        1. All the partials that make up the complete item

        We can generate
        1. The bounding box
        2. The meta
        3. The aligned axis
        4. The relative (choose the partial item with max area )
        5. The absolute
        """
        if not partial_items:
            raise ValueError(
                "Cannot generate information on empty list of partial items"
            )

        # checking for uniformity
        _axis = [p_item.absolute.aligned_axis for p_item in partial_items]
        is_unified_axis = (
            False if len(_axis) == 0 else _axis.count(_axis[0]) == len(_axis)
        )
        if not is_unified_axis:
            raise ValueError("Partial items do not have a unified axis")

        _aisle_index = [p_item.meta.aisle_index for p_item in partial_items]
        is_unified_aisle_index = (
            False
            if len(_aisle_index) == 0
            else _aisle_index.count(_aisle_index[0]) == len(_aisle_index)
        )
        if not is_unified_aisle_index:
            raise ValueError("Partial items do not have a unified aisle index")

        _item_type = [p_item.meta.item_type for p_item in partial_items]
        is_unified_item_type = (
            False
            if len(_item_type) == 0
            else _item_type.count(_item_type[0]) == len(_item_type)
        )
        if not is_unified_item_type:
            raise ValueError("Partial items do not have a unified item type")

        _scan_id = [p_item.meta.scan_id for p_item in partial_items]
        is_unified_scan_id = (
            False
            if len(_scan_id) == 0
            else _scan_id.count(_scan_id[0]) == len(_scan_id)
        )
        if not is_unified_scan_id:
            raise ValueError("Partial items do not have a unified scan id")

        # # Populate meta. start with basic item meta
        item_meta = ItemMeta(
            item_type=_item_type[0],
            location="inventory",
            available=True,
            aisle_index=_aisle_index[0],
            scan_id=_scan_id[0],
        )

        # selecting the ideal partial item
        def _get_area(p_item: PartialItem) -> float:
            return RectangleService.get_area(p_item.bounding_box)

        _ideal_partial_item = partial_items[0]
        for p_item in partial_items[1:]:
            if _get_area(p_item) > _get_area(_ideal_partial_item):
                _ideal_partial_item = p_item

        item_relative = ItemRelative(
            header=_ideal_partial_item.relative.header,
            position=_ideal_partial_item.relative.position,
            dimension=_ideal_partial_item.relative.dimension,
            side=_ideal_partial_item.relative.side,
        )

        min_bottom_left_x, min_bottom_left_y = np.inf, np.inf
        max_top_right_x, max_top_right_y = -np.inf, -np.inf
        for p_item in partial_items:
            rect = p_item.bounding_box
            min_bottom_left_x = min(min_bottom_left_x, rect.bottom_left.x)
            min_bottom_left_y = min(min_bottom_left_y, rect.bottom_left.y)
            max_top_right_x = max(max_top_right_x, rect.top_right.x)
            max_top_right_y = max(max_top_right_y, rect.top_right.y)

        item_bounding_box = Rectangle(
            bottom_left=Vector2(x=min_bottom_left_x, y=min_bottom_left_y),
            top_right=Vector2(x=max_top_right_x, y=max_top_right_y),
        )
        dimension = Vector3(
            x=abs(item_bounding_box.top_right.x - item_bounding_box.bottom_left.x),
            y=abs(item_bounding_box.top_right.y - item_bounding_box.bottom_left.y),
            z=0,
        )
        item_relative = ItemRelative(
            header=_ideal_partial_item.relative.header,
            # this can be poopulated with anything, it is not used
            position=_ideal_partial_item.relative.position,
            dimension=dimension,
            side=_ideal_partial_item.relative.side,
        )

        _bottom_center_point = RectangleService.get_bottom_center_point(
            item_bounding_box
        )
        # Populate absolute
        item_absolute = ItemAbsolute(
            position=Vector3(
                x=_bottom_center_point.x,
                y=_bottom_center_point.y,
                z=_ideal_partial_item.absolute.position.z,
            ),
            dimension=dimension,
            aligned_axis=_ideal_partial_item.absolute.aligned_axis,
        )
        return Item(meta=item_meta, absolute=item_absolute, relative=item_relative)

    @classmethod
    def generate_item_stack(cls, items: list[Item]) -> dict[str, list[str]]:
        """Method to generate stack map for all the items."""
        stack_graph: dict[str, set[str]] = defaultdict(set)

        for i, item1 in enumerate(items):
            for _, item2 in enumerate(items[i + 1 :], start=i + 1):
                rect1 = item1.bounding_box
                rect2 = item2.bounding_box

                if RectangleService.is_stacked_on(rect1, rect2):
                    stack_graph[item2.uuid].add(item1.uuid)
                elif RectangleService.is_stacked_on(rect2, rect1):
                    stack_graph[item1.uuid].add(item2.uuid)

        return {key: list(val) for key, val in stack_graph.items()}

    @classmethod
    def combine_barcodes(cls, items: list[Item], barcodes: list[Barcode]) -> list[Item]:
        """Method to combine barcodes with item.."""
        # Currently bruce forcing (very expensive) TODO use Rtrees
        for barcode in barcodes:
            for item in items:
                # Check that the barcode is completely inside the item
                item_bb = item.bounding_box
                barcode_bb = barcode.bounding_box
                item_contains_barcode = RectangleService.contains_point(
                    item_bb, barcode_bb.bottom_left.x, barcode_bb.bottom_left.y
                ) and RectangleService.contains_point(
                    item_bb, barcode_bb.top_right.x, barcode_bb.top_right.y
                )

                if item_contains_barcode:
                    item.barcodes.append(barcode)
                    barcode.item_uuid = item.uuid

                    # Save some computation by breaking early
                    # A barcode can only be inside one item
                    break

        return items
