from .person import Person
from datetime import time

class Child(Person):

    def build_general_schedule(self):
        self.schedule = [
            {"start_time": time(7, 0), "start_waypoint": "home", "end_waypoint": "school"},
            {"start_time": time(13, 0), "start_waypoint": "school", "end_waypoint": "home"},
            {"start_time": time(15, 0), "start_waypoint": "home", "end_waypoint": "park"},
            {"start_time": time(18, 0), "start_waypoint": "park", "end_waypoint": "home"},
        ]
        return self.schedule