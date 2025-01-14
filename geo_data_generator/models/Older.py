from .person import Person
from datetime import time

class Older(Person):

    def build_general_schedule(self):
        self.schedule = [
            {"start_time": time(8, 0), "start_waypoint": "home", "end_waypoint": "park"},
            {"start_time": time(10, 0), "start_waypoint": "park", "end_waypoint": "healthcare"},
            {"start_time": time(12, 0), "start_waypoint": "healthcare", "end_waypoint": "home"},
            {"start_time": time(16, 0), "start_waypoint": "home", "end_waypoint": "park"},
            {"start_time": time(19, 0), "start_waypoint": "park", "end_waypoint": "home"},
        ]
        return self.schedule