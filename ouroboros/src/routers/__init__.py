# Copyright 2024 The Rubic. All Rights Reserved.

from .batch import batch_router
from .inventory import inventory_router
from .robot import robot_router
from .scan import scan_router

__all__ = ["batch_router", "inventory_router", "robot_router", "scan_router"]
