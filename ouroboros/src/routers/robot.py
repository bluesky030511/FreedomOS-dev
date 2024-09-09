# Copyright 2024 The Rubic. All Rights Reserved.

"""For routing messages to the robot."""

from faststream.rabbit.router import RabbitRouter

robot_router = RabbitRouter(prefix="robot/")
