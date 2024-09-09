# ruff: noqa: PGH004
# ruff: noqa
from datetime import UTC, datetime

from bson import ObjectId

from db.mongodb import (
    partial_barcode_collection,
    partial_item_collection,
    scan_image_collection,
)
from src.models import Barcode, PartialItem
from src.models.db import ScanImage
from src.utils import validate_many_docs

BASE_SCAN_ID = "11913c50-728c-4ba2-a26f-84b09b2eeb78"
NEW_SCAN_ID = "6e59b349-b3fc-49d4-9255-eb147ae5c748"
MIN_DATE = datetime(year=2024, month=8, day=3, tzinfo=UTC)
X_START = 51
X_END = 55
Y_START = 0
Y_END = 3.5


def update_partial_items():
    partial_items_doc = partial_item_collection.find({"meta.scan_id": BASE_SCAN_ID})
    partial_items = validate_many_docs(partial_items_doc, PartialItem)
    for x in partial_items:
        generation_time = x.object_id.generation_time  # pyright: ignore[reportAttributeAccessIssue]
        if generation_time > MIN_DATE:
            print(generation_time)
            x.meta.scan_id = NEW_SCAN_ID

            doc = x.model_dump()
            query = {"_id": x.object_id}
            new_values = {"$set": doc}
            update_result = partial_item_collection.update_one(query, new_values)


def update_partial_barcodes():
    partial_barcodes_doc = partial_barcode_collection.find(
        {"meta.scan_id": BASE_SCAN_ID}
    )
    partial_barcodes = validate_many_docs(partial_barcodes_doc, Barcode)
    for x in partial_barcodes:
        generation_time = x.object_id.generation_time  # pyright: ignore[reportAttributeAccessIssue]
        if generation_time > MIN_DATE:
            print(generation_time)
            x.meta.scan_id = NEW_SCAN_ID

            doc = x.model_dump()
            query = {"_id": x.object_id}
            new_values = {"$set": doc}
            update_result = partial_barcode_collection.update_one(query, new_values)


def update_scan_images():
    scan_images_doc = scan_image_collection.find({"scan_id": BASE_SCAN_ID})
    scan_images = validate_many_docs(scan_images_doc, ScanImage)
    for x, y in zip(scan_images, scan_images_doc):
        generation_time = datetime.fromtimestamp(x.stamp.sec, tz=UTC)
        if generation_time > MIN_DATE:
            print(generation_time)
            x.scan_id = NEW_SCAN_ID

            doc = x.model_dump()
            query = {"_id": ObjectId(y["_id"])}
            new_values = {"$set": doc}
            update_result = scan_image_collection.update_one(query, new_values)


def delete_partial_items():
    partial_items_doc = partial_item_collection.find({"meta.scan_id": BASE_SCAN_ID})
    partial_items = validate_many_docs(partial_items_doc, PartialItem)
    for item in partial_items:
        if (
            X_START < item.absolute.position.x < X_END
            and Y_START < item.absolute.position.y < Y_END
        ):
            query = {"_id": item.object_id}
            partial_item_collection.delete_one(query)


def delete_partial_barcodes():
    partial_barcodes_doc = partial_barcode_collection.find(
        {"meta.scan_id": BASE_SCAN_ID}
    )
    partial_barcodes = validate_many_docs(partial_barcodes_doc, Barcode)
    for barcode in partial_barcodes:
        if (
            X_START < barcode.absolute.position.x < X_END
            and Y_START < barcode.absolute.position.y < Y_END
        ):
            query = {"_id": barcode.object_id}
            partial_barcode_collection.delete_one(query)


def delete_scan_items():
    scan_images_doc = scan_image_collection.find({"scan_id": BASE_SCAN_ID})
    scan_images = validate_many_docs(scan_images_doc, ScanImage)
    for image, image_doc in zip(scan_images, scan_images_doc):
        if (
            X_START < image.image_bottom_left.x < X_END
            and Y_START < image.image_bottom_left.y < Y_END
        ):
            query = {"_id": ObjectId(image_doc["_id"])}
            scan_image_collection.delete_one(query)


if __name__ == "__main__":
    # update_partial_items()
    # update_partial_barcodes()
    # update_scan_images()

    delete_partial_items()
    delete_partial_barcodes()
    delete_scan_items()
