# Copyright 2024 The Rubic. All Rights Reserved.

"""Configuration file for environment variables."""

import logging
import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv

logger = logging.getLogger("__main__")

load_dotenv()

key_vault_name = "RubicKeyVault"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
credential = DefaultAzureCredential()
az_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# RabbitMQ env
AMQP_CONN_STR = os.environ.get("AMQP_SSL_CONN_STR")
if AMQP_CONN_STR is None:
    AMQP_CONN_STR = az_client.get_secret("AMQP-SSL-CONN-STR").value
if not AMQP_CONN_STR:
    raise ValueError(
        "AMQP-SSL-CONN-STR environment variable not found. "
        "Using default connection string."
    )

# Mongo DB env
mongo_db_conn_str = os.environ.get("MONGODB_CONN_STR")
if mongo_db_conn_str is None:
    mongo_db_conn_str = az_client.get_secret("MONGODB-CONN-STR").value
if not mongo_db_conn_str:
    logger.warning(
        "MONGODB-CONN-STR environment variable not found. "
        "Using default connection string."
    )
    mongo_db_conn_str = "mongodb://localhost:27017/"
MONGO_CONN_STR = mongo_db_conn_str

# Azure Blob env
AZUR_BLOB_CONN = az_client.get_secret("AZURE-BLOB-CONN").value
if AZUR_BLOB_CONN is None:
    raise ValueError(
        "AZURE-BLOB-CONN environment variable not found. "
        "Using default connection string."
    )
