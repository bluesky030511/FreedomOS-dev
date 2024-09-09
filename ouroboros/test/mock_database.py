# Copyright 2024 The Rubic. All Rights Reserved.

from pathlib import Path

import mongomock
from bson.json_util import loads

FILE_PATH = Path(__file__).parent

MOCK_CLIENT = mongomock.MongoClient()

for folder in (FILE_PATH / "data").glob("*"):
    db = MOCK_CLIENT[folder.name]
    for file in folder.glob("*"):
        collection = db[file.stem]
        data = loads(file.read_text())
        collection.insert_many(data)
