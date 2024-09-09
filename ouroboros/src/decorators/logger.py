# Copyright 2024 The Rubic. All Rights Reserved.

"""Logger wrapper."""

import functools
import traceback
from collections.abc import Callable

from loguru import logger


def log(func: Callable) -> Callable:
    """Logger wrapper."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> None:
        logger.log("INFO", "Started '{}' with args: {}", func.__name__, (args, kwargs))

        try:
            result = await func(*args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())
            raise

        logger.log("INFO", "Ended '{}' with result: {}", func.__name__, result)
        return result

    return wrapper
