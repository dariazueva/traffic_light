import random
from collections import deque

import simpy

DEFAULT_GREEN_TIME = 20
PEDESTRIAN_GREEN_TIME = 10
QUEUE_THRESHOLD = 5
EXTEND_GREEN_TIME = 30


class TrafficLight:
    def __init__(self, env, id, light_type, all_lights):
        self.env = env
        self.id = id
        self.light_type = light_type
        self.queue_length = 0
        self.state = "red" if light_type == "cars" else "green"
        self.timer = (
            DEFAULT_GREEN_TIME if light_type == "cars" else PEDESTRIAN_GREEN_TIME
        )
        self.all_lights = all_lights
        self.action = env.process(self.run())
        self.env.process(self.update_queue_periodically())

    def update_queue_periodically(self):
        while True:
            if self.light_type == "cars":
                self.queue_length += random.randint(0, 5)
            elif self.light_type == "pedestrians":
                self.queue_length += random.randint(0, 3)
            yield self.env.timeout(10)

    def run(self):
        while True:
            self.evaluate_state()
            if self.state == "red":
                self.state = "green"
                print(
                    f"Светофор {self.id} переключился на зеленый в момент {self.env.now}, очередь: {self.queue_length}"
                )
            elif self.state == "green":
                if self.light_type == "cars":
                    self.state = "yellow"
                    print(
                        f"Светофор {self.id} переключился на желтый в момент {self.env.now}"
                    )
                else:
                    self.state = "red"
                    print(
                        f"Светофор {self.id} переключился на красный в момент {self.env.now}"
                    )
            elif self.state == "yellow":
                self.state = "red"
                print(
                    f"Светофор {self.id} переключился на красный в момент {self.env.now}"
                )
            yield self.env.timeout(self.timer)
            if self.state == "green" and self.queue_length > 0:
                self.queue_length -= 1
                print(
                    f'Светофор {self.id} пропустил 1 {"машину" if self.light_type == "cars" else "пешехода"}, очередь: {self.queue_length}'
                )

    def evaluate_state(self):
        if self.queue_length > QUEUE_THRESHOLD:
            self.timer = (
                EXTEND_GREEN_TIME
                if self.light_type == "cars"
                else PEDESTRIAN_GREEN_TIME + 5
            )
        else:
            self.timer = (
                DEFAULT_GREEN_TIME
                if self.light_type == "cars"
                else PEDESTRIAN_GREEN_TIME
            )
        for other_light in self.all_lights:
            if other_light.id != self.id:
                other_state = other_light.state
                print(
                    f"Светофор {self.id} получил информацию о состоянии от светофора {other_light.id}"
                )
                if (
                    other_state == "green"
                    and other_light.queue_length > QUEUE_THRESHOLD
                ):
                    self.timer = max(self.timer, EXTEND_GREEN_TIME)


env = simpy.Environment()


traffic_lights = []
for i in range(4):
    traffic_light = TrafficLight(
        env, id=i, light_type="cars", all_lights=traffic_lights
    )
    traffic_lights.append(traffic_light)

for i in range(4, 12):
    traffic_light = TrafficLight(
        env, id=i, light_type="pedestrians", all_lights=traffic_lights
    )
    traffic_lights.append(traffic_light)

env.run(until=30)
