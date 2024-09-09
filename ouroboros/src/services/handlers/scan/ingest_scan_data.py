# Copyright 2024 The Rubic. All Rights Reserved.

"""ScanData handler."""

import base64
import io

from azure.storage.blob import BlobServiceClient
from faststream.rabbit.annotations import Logger

from config import settings
from db.mongodb import (
    partial_barcode_collection,
    partial_item_collection,
    scan_image_collection,
)
from src.models import ScanData
from src.services.handlers import Handler


class IngestScanData(Handler):
    """ScanData handler."""

    async def run(self, body: ScanData, logger: Logger) -> None:  # noqa: PLR6301
        """Ingest ScanData message."""
        result = body

        logger.info(
            "Received ScanData with {} partial items item(s) and "
            "{} barcodes for scan_id {}",
            len(result.partial_items),
            len(result.barcodes),
            result.scan_id,
        )

        inserted_img = scan_image_collection.insert_one(
            result.model_dump(exclude={"partial_items", "barcodes"})
        )
        for item in result.partial_items:
            item.meta.image_id = inserted_img.inserted_id
            item.meta.scan_id = result.scan_id
            partial_item_collection.insert_one(item.model_dump())

        for barcode in result.barcodes:
            barcode.meta.image_id = inserted_img.inserted_id
            barcode.meta.scan_id = result.scan_id
            partial_barcode_collection.insert_one(barcode.model_dump())

        logger.info(
            "Inserted ScanData to database with {} partial items and {} barcodes",
            len(result.partial_items),
            len(result.barcodes),
        )

        img_str = result.image
        webp_bytes = bytes(img_str, "utf-8")
        webp_byte_b64 = base64.b64decode(webp_bytes)
        webp_bytes_io = io.BytesIO(webp_byte_b64)
        webp_byte_size = webp_bytes_io.getbuffer().nbytes

        if webp_byte_size > 0 and result.image_filename:
            container = "scan-images-raw"
            blob_name = result.image_filename + f"_{result.scan_id}.webp"
            blob_service_client = BlobServiceClient.from_connection_string(
                settings.AZUR_BLOB_CONN  # pyright: ignore[reportArgumentType]
            )
            container_client = blob_service_client.get_container_client(
                container=container
            )
            container_client.upload_blob(
                name=blob_name, data=webp_bytes_io, overwrite=False
            )

            logger.info("Uploaded scan image to Azure ({} b)", webp_byte_size)
