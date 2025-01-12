from .Person import Person
from datetime import time

class Adult(Person):
    def assign_waypoints(self):
        self.assign_home()
        self.assign_workplace()
        self.assign_gym()
        self.assign_market()

    def assign_home(self):
        super().assign_home()

    def assign_workplace(self):
        super().assign_workplace()

    def assign_gym(self):
        super().assign_gym()

    def assign_market(self):
        super().assign_market()



    def build_general_schedule(self):
        """
        Build a general schedule for an adult person using general times.
        """
        return [
            {"start_time": time(7, 0), "start_waypoint": "home", "end_waypoint": "workplace"},
            {"start_time": time(12, 0), "start_waypoint": "workplace", "end_waypoint": "market"},
            {"start_time": time(13, 0), "start_waypoint": "market", "end_waypoint": "workplace"},
            {"start_time": time(18, 0), "start_waypoint": "workplace", "end_waypoint": "gym"},
            {"start_time": time(20, 0), "start_waypoint": "gym", "end_waypoint": "home"},
        ]