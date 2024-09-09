# Copyright 2024 The Rubic. All Rights Reserved.

"""Render inventory handler."""

import base64
import io
import math
import time

import numpy as np
from azure.storage.blob import BlobServiceClient
from faststream.annotations import Logger
from loguru import logger
from PIL import Image

from config import settings
from db.mongodb import (
    inventory_items,
    partial_item_collection,
    renders_collection,
    scan_image_collection,
)
from src.models import (
    Item,
    ItemAbsolute,
    ItemMeta,
    ItemRelative,
    PartialItem,
    Render,
    RenderImageMeta,
    RenderItemData,
    RenderMeta,
    RenderScanRequest,
    ScanImage,
)
from src.services.handlers import Handler
from src.services.model.item import ItemService
from src.utils import validate_many_docs


class RenderInventory(Handler):
    """RenderInventory outputs and stores the render of the current inventory."""

    scan_images_blob_container = "scan-images"
    blob_service_client = BlobServiceClient.from_connection_string(
        settings.AZUR_BLOB_CONN  # pyright: ignore[reportArgumentType]
    )
    container_client = blob_service_client.get_container_client(
        scan_images_blob_container
    )

    # service
    item_service = ItemService()

    async def run(self, body: RenderScanRequest, logger: Logger) -> None:
        """Function callback when request has been received."""
        to_render_types = ["empty", "box"]
        to_render_sides = ["left", "right"]

        # filter out for empty string
        scan_ids = inventory_items.distinct(
            "meta.scan_id", {"meta.scan_id": {"$ne": ""}}
        )

        for scan_id in scan_ids:
            for side in to_render_sides:
                aisles_indexes = scan_image_collection.distinct(
                    "aisle_index", {"scan_id": scan_id}
                )
                for aisle_index in aisles_indexes:
                    scan_images_docs = scan_image_collection.find(
                        {
                            "side": side,
                            "scan_id": scan_id,
                            "aisle_index": aisle_index,
                        }
                    )
                    scan_images = validate_many_docs(scan_images_docs, ScanImage)
                    render_image_meta = None
                    if scan_images:
                        logger.info(
                            "Found {} scan images for side {}", len(scan_images), side
                        )
                        render_image_meta = self.render_image(scan_images)

                    traces: list[RenderItemData] = []

                    for item_type in to_render_types:
                        # draw rectangles
                        if not body.debug:
                            traces += self.render_item_trace(
                                side, item_type, aisle_index
                            )
                        else:
                            traces += self.render_trace_debug(
                                side, item_type, scan_id, aisle_index
                            )

                    logger.info(
                        "Added render trace with {} data entries for {} side.",
                        len(traces),
                        side,
                    )

                    render = Render(
                        request=body,
                        meta=RenderMeta(side=side, aisle_index=aisle_index),
                        data=traces,
                        img_meta=render_image_meta,
                    )

                    # save to mongodb
                    renders_collection.delete_many(
                        {"meta.side": side, "meta.aisle_index": aisle_index}
                    )
                    renders_collection.insert_one(render.model_dump())
                    logger.info("Saved {} side render to mongodb", side)

    @classmethod
    def render_image(cls, scan_image_models: list[ScanImage]) -> RenderImageMeta:
        """Render image for a given side and scan id."""
        logger.info("Rendering inventory requested for image. Generating image...")
        min_x, max_x, min_y, max_y = math.inf, -math.inf, math.inf, -math.inf

        images = []
        coordinates = []

        for scan_image_model in scan_image_models:
            img_str = scan_image_model.image
            if not img_str:
                continue

            jpg_bytes = bytes(img_str, "utf-8")
            jpg_byte_b64 = base64.b64decode(jpg_bytes)
            jpg_bytes_io = io.BytesIO(jpg_byte_b64)
            img = Image.open(jpg_bytes_io)

            # check if the image is inverted
            is_inverted = (
                scan_image_model.image_bottom_left.x
                > scan_image_model.image_top_right.x
            )
            if is_inverted:
                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                # swap x coordinates
                (
                    scan_image_model.image_bottom_left.x,
                    scan_image_model.image_top_right.x,
                ) = (
                    scan_image_model.image_top_right.x,
                    scan_image_model.image_bottom_left.x,
                )
            min_x = min(min_x, scan_image_model.image_bottom_left.x)
            min_y = min(min_y, scan_image_model.image_bottom_left.y)
            max_x = max(max_x, scan_image_model.image_top_right.x)
            max_y = max(max_y, scan_image_model.image_top_right.y)

            images.append(img)
            coordinates.append(
                (
                    scan_image_model.image_bottom_left.x,
                    scan_image_model.image_bottom_left.y,
                    scan_image_model.image_top_right.x,
                    scan_image_model.image_top_right.y,
                )
            )

        render = cls.stack_images(images, coordinates, (min_x, min_y, max_x, max_y))
        buf = io.BytesIO()
        render.save(buf, format="JPEG", quality=80)
        logger.info("Render image saved to buffer")

        # save to Azure
        blob_name = f"inventory_render_{time.time()}.jpg"
        cls.container_client.upload_blob(name=blob_name, data=buf.getvalue())
        logger.info(
            "Uploaded render image to Azure with filename "
            f"{blob_name} ({buf.getbuffer().nbytes} bytes)"
        )

        width = abs(max_x - min_x)
        height = abs(max_y - min_y)
        # build image data in pydantic
        return RenderImageMeta(
            x=min_x,
            y=max_y,
            width=width,
            height=height,
            container_name=cls.scan_images_blob_container,
            blob_name=blob_name,
        )

    @staticmethod
    def stack_images(
        images: list[Image.Image],
        coordinates: list[tuple[float, float, float, float]],
        bounds: tuple[float, float, float, float],
        pixels_per_meter: int = 400,
    ) -> Image.Image:
        """Stack images into a single image with given coordinates and bounds."""
        min_x, min_y, max_x, max_y = bounds
        canvas_width = math.ceil((max_x - min_x) * pixels_per_meter)
        canvas_height = math.ceil((max_y - min_y) * pixels_per_meter)
        canvas = np.full((canvas_height, canvas_width), 255, dtype=np.uint8)

        def pos_to_pixel(x: float, y: float) -> tuple[int, int]:
            new_x = round((x - min_x) * pixels_per_meter)
            new_y = round((y - min_y) * pixels_per_meter)
            return new_x, new_y

        for (x0, y0, x1, y1), im in zip(coordinates, images, strict=False):
            _x0, _y0 = pos_to_pixel(x0, y0)
            _x1, _y1 = pos_to_pixel(x1, y1)

            width = _x1 - _x0
            height = _y1 - _y0
            _y0, _y1 = canvas_height - _y1, canvas_height - _y0

            patch_im = im.resize((width, height), resample=Image.Resampling.BILINEAR)
            mask_im = im.resize((width, height), resample=Image.Resampling.NEAREST)

            patch = np.array(patch_im)[:, :, 0]
            mask = np.array(mask_im)[:, :, 3].astype(bool)

            canvas[_y0:_y1, _x0:_x1] = np.where(mask, patch, canvas[_y0:_y1, _x0:_x1])

        return Image.fromarray(canvas)

    @classmethod
    def render_item_trace(
        cls, side: str, item_type: str, aisle_index: int
    ) -> list[RenderItemData]:
        """Render trace for a given side and item type."""
        items_doc = inventory_items.find(
            {
                "relative.side": side,
                "meta.item_type": item_type,
                "meta.location": "inventory",
                "meta.available": True,
                "meta.aisle_index": aisle_index,
            }
        )
        items = validate_many_docs(items_doc, Item)

        # To reduce time for adding shapes:
        # https://stackoverflow.com/questions/70276242/adding-500-circles-in-a-plotly-graph-using-add-shape-function-takes-45-seconds
        logger.info(f"Creating {len(items)} shape traces for items of type {item_type}")
        return [
            RenderItemData(
                item=item,
                x0=item.bounding_box.bottom_left.x,
                y0=item.bounding_box.bottom_left.y,
                x1=item.bounding_box.top_right.x,
                y1=item.bounding_box.top_right.y,
            )
            for item in items
        ]

    @staticmethod
    def render_trace_debug(
        side: str, item_type: str, scan_id: str, aisle_index: int
    ) -> list[RenderItemData]:
        """Render trace debug for a given side and item type."""
        partial_items_doc = partial_item_collection.find(
            {
                "meta.item_type": item_type,
                "meta.scan_id": scan_id,
                "meta.confidence": {"$gte": 0.15},
                "relative.side": side,
                "absolute.dimension.x": {"$gte": 0.08},
                "meta.aisle_index": aisle_index,
            }
        )
        partial_items = validate_many_docs(partial_items_doc, PartialItem)

        return [
            RenderItemData(
                item=Item(
                    meta=ItemMeta(
                        item_type="DEBUG",
                        stack=[],
                        location="inventory",
                        destination=None,
                        available=False,
                    ),
                    relative=ItemRelative.model_validate(
                        partial_item.relative.model_dump()
                    ),
                    absolute=ItemAbsolute.model_validate(
                        partial_item.absolute.model_dump()
                    ),
                    barcodes=[],
                ),
                x0=partial_item.bounding_box.bottom_left.x,
                y0=partial_item.bounding_box.bottom_left.y,
                x1=partial_item.bounding_box.top_right.x,
                y1=partial_item.bounding_box.top_right.y,
            )
            for partial_item in partial_items
        ]
