import random
from collections import deque

import simpy

DEFAULT_GREEN_TIME = 20
PEDESTRIAN_GREEN_TIME = 10
QUEUE_THRESHOLD = 5
EXTEND_GREEN_TIME = 30


class Event:
    def __init__(self, sender_id, queue_length, state):
        self.sender_id = sender_id
        self.queue_length = queue_length
        self.state = state


class TrafficLight:
    def __init__(self, env, id, light_type):
        self.env = env
        self.id = id
        self.light_type = light_type
        self.queue_length = 0
        self.state = "red" if light_type == "cars" else "green"
        self.timer = (
            DEFAULT_GREEN_TIME if light_type == "cars" else PEDESTRIAN_GREEN_TIME
        )
        self.events = deque()
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
            self.send_event_to_neighbors()
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
                    f'Светофор {self.id} пропустил 1 {"cars" if self.light_type == "cars" else "pedestrians"}, очередь: {self.queue_length}'
                )
            self.process_events()

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

    def send_event_to_neighbors(self):
        event = Event(self.id, self.queue_length, self.state)

    def process_events(self):
        while self.events:
            event = self.events.popleft()
            print(
                f"Светофор {self.id} получил событие от светофора {event.sender_id}: очередь {event.queue_length}, состояние {event.state}"
            )


env = simpy.Environment()


traffic_lights = [TrafficLight(env, id=i, light_type="cars") for i in range(4)] + [
    TrafficLight(env, id=i, light_type="pedestrians") for i in range(8)
]

env.run(until=30)
