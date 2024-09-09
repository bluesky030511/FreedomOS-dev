# Copyright 2024 The Rubic. All Rights Reserved.

"""Script to convert nested MongoDB documents Postgres."""

import re
import sys
import time
import uuid

import psycopg2
import pymongo
from psycopg2.extras import Json, execute_batch, register_uuid
from pymongo.server_api import ServerApi


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, psycopg2.extras.Json(v)))
        else:
            items.append((new_key, v))
    return dict(items)


def sanitize_column_name(name):
    # Replace invalid characters and trim length
    return re.sub(r"\W+", "_", name)


# MongoDB connection parameters


mongo_params = {
    "host": "your_mongo_host",
    "port": 27017,
    "db": "your_mongo_db",
    "collection": "your_mongo_collection",
}

# PostgreSQL connection parameters
pg_params = {
    "host": "localhost",
    "port": "5432",
    "database": "rubic",
    "user": "developer",
    "password": "rubicdeveloper",
}

# Batch size for processing
BATCH_SIZE = 1000


if __name__ == "__main__":
    db_name = "inventory_items"

    print(f"Converting MongoDB collection '{db_name}' to PostgreSQL table '{db_name}'")

    # Connect to MongoDB
    mongo_client = pymongo.MongoClient(
        "mongodb+srv://bxia:1_Hard_Password_!@cluster0.w5tznvy.mongodb.net/Orbit?retryWrites=true&w=majority&appName=Cluster0",
        server_api=ServerApi("1"),
    )

    mongo_db = mongo_client["Orbit"]
    mongo_collection = mongo_db[db_name]

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(**pg_params)
    pg_cur = pg_conn.cursor()

    # Register UUID type with psycopg2
    register_uuid()

    try:
        # Drop the table if it exists
        drop_table_query = f"DROP TABLE IF EXISTS {db_name};"
        pg_cur.execute(drop_table_query)
        pg_conn.commit()
        print(f"Dropped table {db_name} if it existed.")

        # Scan multiple documents to build a more comprehensive schema
        schema = {}
        null_tracker = {}
        for doc in mongo_collection.find(
            {"meta.item_type": {"$ne": "conveyor"}}
        ):  # Scan up to 100 documents
            flattened = flatten_dict(doc)
            for key, value in flattened.items():
                if key not in schema:
                    if value is None:
                        schema[key] = "TEXT"
                        null_tracker[key] = True

                    elif isinstance(value, bool):
                        schema[key] = "BOOLEAN"
                    elif isinstance(value, int):
                        schema[key] = "INTEGER"
                    elif isinstance(value, float):
                        schema[key] = "FLOAT"
                    elif isinstance(value, list) or isinstance(value, Json):
                        # schema[key] = "JSONB"
                        pass
                    else:
                        schema[key] = "TEXT"

                    if key not in null_tracker:
                        null_tracker[key] = False
                elif value is None:
                    null_tracker[key] = True

        # Prepare CREATE TABLE statement
        columns = [
            "id UUID PRIMARY KEY DEFAULT gen_random_uuid()",
            "mongo_id TEXT NOT NULL",
        ]
        column_mapping = {"_id": "mongoId"}
        for key, data_type in schema.items():
            if key == "_id":
                continue
            sanitized_key = sanitize_column_name(key)
            nullable = " NULL" if null_tracker[key] else " NOT NULL"
            columns.append(f'"{sanitized_key}" {data_type}{nullable}')
            column_mapping[key] = sanitized_key

        create_table_query = f"""
        CREATE TABLE {db_name} (
            {', '.join(columns)}
        );
        """
        pg_cur.execute(create_table_query)

        # Prepare the insert query
        insert_columns = [
            col.split()[0].strip('"') for col in columns if col.split()[0] != "id"
        ]
        insert_placeholders = ", ".join(["%s"] * len(insert_columns))
        insert_query = f"INSERT INTO {db_name} ({', '.join(insert_columns)}) VALUES ({insert_placeholders})"

        total_docs = mongo_collection.count_documents(
            {"meta.item_type": {"$ne": "conveyor"}}
        )
        print(f"Total documents to process: {total_docs}")

        start_time = time.time()
        processed_docs = 0

        # Process documents in batches
        for i in range(0, total_docs, BATCH_SIZE):
            batch = list(
                mongo_collection.find({"meta.item_type": {"$ne": "conveyor"}})
                .skip(i)
                .limit(BATCH_SIZE)
            )

            # Prepare batch data
            batch_data = []
            for mongo_doc in batch:
                flattened_doc = flatten_dict(mongo_doc)
                row_data = [str(flattened_doc.pop("_id"))]
                for col in insert_columns[1:]:  # Skip mongo_id as it's already added
                    row_data.append(flattened_doc.get(col, None))
                batch_data.append(tuple(row_data))

            # Insert batch into PostgreSQL
            execute_batch(pg_cur, insert_query, batch_data)
            pg_conn.commit()

            processed_docs += len(batch)
            elapsed_time = time.time() - start_time
            docs_per_second = processed_docs / elapsed_time

            print(
                f"Processed {processed_docs}/{total_docs} documents. "
                f"Speed: {docs_per_second:.2f} docs/sec"
            )

        print(f"All documents processed. Total time: {elapsed_time:.2f} seconds")

    except Exception as e:
        print(f"An error occurred: {e}")
        pg_conn.rollback()

    finally:
        # Close connections
        pg_cur.close()
        pg_conn.close()
        mongo_client.close()

    print("Script completed.")
