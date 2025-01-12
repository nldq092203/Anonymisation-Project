from .Person import Person
from datetime import time

class Child(Person):
    def assign_waypoints(self):
        self.assign_home()
        self.assign_school()
        self.assign_park()

    def assign_home(self):
        super().assign_home()

    def assign_school(self):
        super().assign_school()

    def assign_park(self):
        super().assign_park()

    def build_general_schedule(self):
        return [
            {"start_time": time(7, 0), "start_waypoint": "home", "end_waypoint": "school"},
            {"start_time": time(13, 0), "start_waypoint": "school", "end_waypoint": "home"},
            {"start_time": time(15, 0), "start_waypoint": "home", "end_waypoint": "park"},
            {"start_time": time(18, 0), "start_waypoint": "park", "end_waypoint": "home"},
        ]