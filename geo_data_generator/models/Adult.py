from .person import Person
from datetime import time

class Adult(Person):

    def build_general_schedule(self):
        """
        Build a general schedule for an adult person using general times.
        """
        self.schedule = [
            {"start_time": time(7, 0), "start_waypoint": "home", "end_waypoint": "workplace"},
            {"start_time": time(12, 0), "start_waypoint": "workplace", "end_waypoint": "market"},
            {"start_time": time(13, 0), "start_waypoint": "market", "end_waypoint": "workplace"},
            {"start_time": time(18, 0), "start_waypoint": "workplace", "end_waypoint": "gym"},
            {"start_time": time(20, 0), "start_waypoint": "gym", "end_waypoint": "home"},
        ]
        return self.schedule