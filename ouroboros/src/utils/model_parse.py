# Copyright 2024 The Rubic. All Rights Reserved.

"""Model validation."""

from typing import Any, TypeVar

from loguru import logger
from pydantic import BaseModel, TypeAdapter, ValidationError

T = TypeVar("T", bound=BaseModel)


def validate_doc(doc: Any, model: type[T]) -> T:
    """Validate the document against the model."""
    try:
        return model.model_validate(doc)
    except ValidationError as exc:
        logger.error(
            "Error while validating document with Model {}: {}", model.__name__, exc
        )
        raise


def validate_many_docs(docs: Any, model: type[T]) -> list[T]:
    """Validate the document against the model."""
    try:
        adapter = TypeAdapter(list[model])
        return adapter.validate_python(docs)
    except ValidationError as exc:
        logger.error(
            "Error while validating document with "
            f"Model list[{model.__name__}]: {exc}"
        )
        raise
