from .Person import Person
from datetime import time

class Older(Person):
    def assign_waypoints(self):
        self.assign_home()
        self.assign_park()
        self.assign_healthcare()

    def assign_home(self):
        super().assign_home()

    def assign_park(self):
        super().assign_park()

    def assign_healthcare(self):
        super().assign_healthcare()

    def build_general_schedule(self):
        return [
            {"start_time": time(8, 0), "start_waypoint": "home", "end_waypoint": "park"},
            {"start_time": time(10, 0), "start_waypoint": "park", "end_waypoint": "healthcare"},
            {"start_time": time(12, 0), "start_waypoint": "healthcare", "end_waypoint": "home"},
            {"start_time": time(16, 0), "start_waypoint": "home", "end_waypoint": "park"},
            {"start_time": time(19, 0), "start_waypoint": "park", "end_waypoint": "home"},
        ]