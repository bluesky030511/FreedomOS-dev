# Copyright 2024 The Rubic. All Rights Reserved.

"""Concrete barcode."""

from __future__ import annotations

import math
import time
from collections import defaultdict

import numpy as np
from loguru import logger

from src.models.db import (
    Barcode,
    BarcodeAbsolute,
    Rectangle,
    Vector2,
    Vector3,
)
from src.services.model.rectangle import RectangleService


class BarcodeService:
    """Barcode services."""

    # TODO: This needs to be split
    @classmethod
    def merge(cls, barcodes: list[Barcode]) -> list[Barcode]:  # noqa: C901
        """Method to merge partial barcodes into completed ones. Completes in O(nm)."""
        logger.info("Merge barcodes from {} partial barcodes", len(barcodes))
        merge_distance = 0.1
        start_time = time.perf_counter()

        batches = cls._batch_barcodes(barcodes)
        lookup_table = {i: set() for i in range(len(barcodes))}
        comparisons = 0

        for i, barcode1 in enumerate(barcodes):
            for j, barcode2 in batches[barcode1.meta.data, barcode1.meta.barcode_type]:
                comparisons += 1

                if i == j:
                    continue

                distance = math.dist(
                    barcode1.absolute.position.to_array(),
                    barcode2.absolute.position.to_array(),
                )

                if distance < merge_distance:
                    lookup_table[i].add(j)
                    lookup_table[j].add(i)

        logger.info("Did {} comparisons to generate lookup table", comparisons)
        lookup_table = dict(lookup_table)

        def dfs(node: int, visited: set, graph: dict[int, set]) -> None:
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
        final_barcodes: list[Barcode] = []
        for node in lookup_table:
            _barcodes: list[Barcode] = [barcodes[idx] for idx in lookup_table[node]]
            _barcodes.append(barcodes[node])

            min_bottom_left_x, min_bottom_left_y = np.inf, np.inf
            max_top_right_x, max_top_right_y = -np.inf, -np.inf
            for _barcode in _barcodes:
                rect = _barcode.bounding_box
                min_bottom_left_x = min(min_bottom_left_x, rect.bottom_left.x)
                min_bottom_left_y = min(min_bottom_left_y, rect.bottom_left.y)
                max_top_right_x = max(max_top_right_x, rect.top_right.x)
                max_top_right_y = max(max_top_right_y, rect.top_right.y)
            new_barcode_bounding_box = Rectangle(
                bottom_left=Vector2(x=min_bottom_left_x, y=min_bottom_left_y),
                top_right=Vector2(x=max_top_right_x, y=max_top_right_y),
            )
            new_barcode_bottom_center = RectangleService.get_bottom_center_point(
                new_barcode_bounding_box
            )

            new_final_barcode = Barcode(
                meta=_barcodes[0].meta,
                absolute=BarcodeAbsolute(
                    position=Vector3(
                        x=new_barcode_bottom_center.x,
                        y=new_barcode_bottom_center.y,
                        z=_barcodes[0].absolute.position.z,
                    ),
                    dimension=Vector3(
                        x=abs(
                            new_barcode_bounding_box.top_right.x
                            - new_barcode_bounding_box.bottom_left.x
                        ),
                        y=abs(
                            new_barcode_bounding_box.top_right.y
                            - new_barcode_bounding_box.bottom_left.y
                        ),
                        z=0,
                    ),
                    aligned_axis=_barcodes[0].absolute.aligned_axis,
                ),
                relative=_barcodes[0].relative,
            )

            final_barcodes.append(new_final_barcode)
        end_time = time.perf_counter()
        duration = end_time - start_time
        logger.info(
            "Generated {} unique barcodes. Took {:.2f}s", len(final_barcodes), duration
        )

        return final_barcodes

    @staticmethod
    def _batch_barcodes(
        barcodes: list[Barcode],
    ) -> dict[tuple[str, str], list[tuple[int, Barcode]]]:
        batches = defaultdict(list)

        for i, barcode in enumerate(barcodes):
            batches[barcode.meta.data, barcode.meta.barcode_type].append((i, barcode))

        return dict(batches)
