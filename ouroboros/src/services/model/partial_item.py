# Copyright 2024 The Rubic. All Rights Reserved.

"""Module containing serializers for database models."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import TYPE_CHECKING

from loguru import logger

from src.services.model.item import ItemService
from src.services.model.rectangle import RectangleService

if TYPE_CHECKING:
    from src.models.db import Item, PartialItem


class PartialItemService:
    """Partial item (box, empty, or barcode are all items)."""

    # TODO: This needs to be split
    @classmethod
    def merge(  # noqa: C901, PLR0912, PLR0915
        cls,
        partial_items: list[PartialItem],
        merge_threshold: float = 0.4,
        distance_threshold: float = 1.5,
    ) -> list[Item]:
        """Method to merge partial items into completed ones. Completes in O(nm)."""
        logger.info("Generating items from {} partial items", len(partial_items))
        start_time = time.perf_counter()

        lookup_table = defaultdict(set)
        non_mergeable = set()
        comparisons = 0

        for i in range(len(partial_items)):
            for j, _ in enumerate(partial_items[i + 1 :], start=i + 1):
                partial_item1, partial_item2 = partial_items[i], partial_items[j]
                if (
                    abs(
                        partial_item1.absolute.position.x
                        - partial_item2.absolute.position.x
                    )
                    <= distance_threshold
                ):
                    # these two items are close enough to have a potential to be
                    # 1. check if they are mergeable, update the look up table
                    comparisons += 1
                    rect1 = partial_item1.bounding_box
                    rect2 = partial_item2.bounding_box
                    rect_overlap_area = RectangleService.get_overlap_area(rect1, rect2)

                    is_mergeable = rect_overlap_area > (
                        merge_threshold * RectangleService.get_area(rect1)
                    ) or rect_overlap_area > (
                        merge_threshold * RectangleService.get_area(rect2)
                    )

                    if is_mergeable:
                        lookup_table[i].add(j)
                        lookup_table[j].add(i)

                        non_mergeable.discard(i)
                        non_mergeable.discard(j)
                    else:
                        non_mergeable.add(i)
                        non_mergeable.add(j)
                else:
                    break

        logger.info("Did {} comparisons to generate lookup table", comparisons)
        lookup_table = dict(lookup_table)

        for i in non_mergeable:
            if i not in lookup_table:
                lookup_table[i] = set()

        def dfs(node: int, visited: set[int], graph: dict[int, set[int]]) -> None:
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, visited, graph)

        # Step 1: Calculate transitive closure for each node
        redundant_edges = set()
        for node in lookup_table:
            if node in redundant_edges:
                continue

            visited: set[int] = set()
            dfs(node=node, visited=visited, graph=lookup_table)
            visited.remove(node)
            # append visited nodes to current lookup_table node
            lookup_table[node] |= visited
            redundant_edges |= visited

        # Step 2: Remove redundant edges
        for node in redundant_edges:
            if node in lookup_table:
                del lookup_table[node]

        logger.info(
            "Removed {} redundant edges, resulting in {} primary edges",
            len(redundant_edges),
            len(lookup_table),
        )

        # Step 3: Convert graph into complete items
        items: list[Item] = []
        for node in lookup_table:
            _partial_items = [partial_items[idx] for idx in lookup_table[node]]
            _partial_items.append(partial_items[node])
            new_complete_item = ItemService.from_partial_items(_partial_items)
            items.append(new_complete_item)

        items.sort(
            key=lambda item: (
                item.bounding_box.bottom_left.x,
                item.bounding_box.bottom_left.y,
            )
        )

        item_count = len(items)

        # Generate stack map TODO
        # Put items in dictionary where uuid is the key and Item is the value
        # Then for each item, set the stack items. Convert it back to a list
        item_lookup = {item.uuid: item for item in items}
        stack = ItemService.generate_item_stack(items)
        for item_uuid, stack_uuids in stack.items():
            item = item_lookup[item_uuid]
            item.meta.stack = stack_uuids
        items = list(item_lookup.values())

        if len(items) != item_count:
            raise RuntimeError("Number of items was modified")

        # Log the end
        end_time = time.perf_counter()
        duration = end_time - start_time
        duration_str = f"{duration:.2f}s"
        logger.info("Generated {} complete items. Took {}", item_count, duration_str)
        return items
