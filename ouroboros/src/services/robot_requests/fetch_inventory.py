# Copyright 2024 The Rubic. All Rights Reserved.

"""Module to implement concrete fetch inventory request."""

from __future__ import annotations

import uuid

from loguru import logger

from src.models import Item, RobotJob

from .base_robot_job_builder import RobotJobBuilderABC


class FetchInventoryRobotJobBuilder(RobotJobBuilderABC):
    """Implements RobotJobBuilder for fetch inventory jobs."""

    def build_jobs(self) -> list[RobotJob]:
        """Build fetch inventory jobs."""
        target_item, items_above = self.get_item_and_stack()

        # This will be the uuid given to the newly created empty item
        # once the below item is fetched
        future_uuid = self.request.destination_uuid or str(uuid.uuid4())
        target_item_job = RobotJob(
            job_type="FETCH_INVENTORY",
            item=target_item,
            future_uuid=future_uuid if items_above else self.request.destination_uuid,
        )

        items_above_fetch_jobs = []
        items_above_store_back_jobs = []
        for item in items_above:
            if item.primary_barcode.meta.data in self.fetched_items:
                if not item.meta.stack:
                    continue
                raise ValueError(
                    "Item was fetched, but has a stack. This is not supported."
                )

            fetch_job = RobotJob(job_type="FETCH_INVENTORY", item=item)
            store_back_job = RobotJob(
                job_type="STORE_INVENTORY",
                item=item,
                destination=self.create_future_empty(future_uuid, target_item),
            )

            items_above_fetch_jobs.append(fetch_job)
            items_above_store_back_jobs.append(store_back_job)

        return [
            *items_above_fetch_jobs,
            target_item_job,
            *items_above_store_back_jobs,
        ]

    def get_item_and_stack(self) -> tuple[Item, list[Item]]:
        """Get item and stack for fetch request."""
        target_item = self.get_item_from_barcode(self.request.uid)

        if len(target_item.meta.stack) > 1:
            raise ValueError(
                f"Multiple items stacked on item with uuid {target_item.uuid}"
            )

        # Add more for stacked items
        # This only handles if there only one item ontop of affected item
        # Make this into a function and call it recursively TODO
        items_above: list[Item] = []
        for stacked_uuid in target_item.meta.stack:
            item_above = self.get_item(stacked_uuid)

            if item_above.meta.stack:
                raise ValueError(f"Found double stacked item, with uuid {stacked_uuid}")

            if item_above.meta.item_type == "empty":
                logger.info("Item with uuid {} is empty. Skipping", stacked_uuid)
                continue

            item_above.primary_barcode = self.get_primary_barcode(stacked_uuid)
            items_above.append(item_above)

        return target_item, items_above
