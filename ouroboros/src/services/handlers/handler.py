# Copyright 2024 The Rubic. All Rights Reserved.

"""Handler class."""

from abc import ABC, abstractmethod
from typing import Any


class Handler(ABC):
    """Abstract class for handler."""

    exc = None

    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """Run handler."""
        raise NotImplementedError
