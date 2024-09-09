import random
import time
from dataclasses import asdict

import schedule
from amqp_publisher import AMQPPublisher
from robot_data import RobotState, RobotStateLowFrequency


class RobotSim:
    def __init__(self):
        self.state = RobotState()
        self.state_low = RobotStateLowFrequency()
        self.pub = AMQPPublisher()
        self.pub.add_exchange("monitor/robot_state")
        self.pub.add_exchange("monitor/robot_state_low")
        self.schedule_events()

    def schedule_events(self):
        schedule.every().second.do(self.publish_state)
        schedule.every(10).seconds.do(self.update_state)
        schedule.every(30).seconds.do(self.publish_state_low)

    def run(self):
        schedule.run_pending()

    def publish_state(self):
        self.pub.publish(asdict(self.state), "monitor/robot_state")

    def publish_state_low(self):
        self.pub.publish(asdict(self.state_low), "monitor/robot_state_low")

    def update_state(self):
        self.state.global_position.x = (
            self.state.global_position.x + random.random()
        ) % 100
        self.state.global_position.y = (
            self.state.global_position.y + random.random()
        ) % 100


if __name__ == "__main__":
    sim = RobotSim()
    while True:
        sim.run()
        time.sleep(1)
