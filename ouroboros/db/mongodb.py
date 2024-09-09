# Copyright 2024 The Rubic. All Rights Reserved.

"""Module for MongoDB connection and collections."""

from dotenv import load_dotenv
from loguru import logger
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from config import settings

load_dotenv()

logger.info("Setting up MongoDB")

conn_str = settings.MONGO_CONN_STR

mongo_client = MongoClient(conn_str, server_api=ServerApi("1"))
try:
    mongo_client.admin.command("ping")
    logger.info(f"MongoDB server ping successful. {conn_str}")
except Exception as e:
    logger.error("Error connecting to MongoDB")
    raise Exception(f"MongoDB server ping failed. {e}") from e


OrbitDB = mongo_client["Orbit"]

partial_item_collection = OrbitDB["partial_item_collection"]
partial_barcode_collection = OrbitDB["partial_barcode_collection"]
low_status_collection = OrbitDB["low_status_collection"]
robot_batch_collection = OrbitDB["robot_batch_collection"]
robot_job_collection = OrbitDB["robot_job_collection"]

barcode_collection = OrbitDB["barcode_collection"]
inventory_items = OrbitDB["inventory_items"]

scan_request_collection = OrbitDB["scan_request"]
scan_image_collection = OrbitDB["scan_image"]


controller_state_collection = OrbitDB["controller_state"]
task_request_collection = OrbitDB["task_request_collection"]

renders_collection = OrbitDB["renders"]

fos_translate_db = mongo_client["FOS_Translate"]
job_type_collection = fos_translate_db["job_type"]
