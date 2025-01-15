
from .waypoint_manager import AutoWaypointAssigner, ManualWaypointAssigner
from datetime import datetime, timedelta, time

class Person:
    def __init__(self, unique_id, person_type, speed, osm_manager, predefined_waypoints={}, schedule=[], detail_schedule=[], mode="automatic"):
        """
        A Person in the simulation with assigned waypoints such as home, workplace, etc.
        
        :param unique_id: Unique identifier for the person.
        :param person_type: 'child', 'adult', or 'older'.
        :param speed: Speed of movement (units can vary based on your simulation).
        :param osm_manager: An OSMManager-like object holding relevant location data.
        :param waypoints: Predefined waypoints, if any (default is None).
        :param schedule: Predefined schedule, if any (default is None).
        :param detail_schedule: Predefined detailed schedule, if any (default is None).
        :param mode: Mode of waypoint assignment ('automatic' or 'self_chosen').
        """
        self.osm_manager = osm_manager
        self.unique_id = unique_id
        self.type = person_type
        self.speed = speed
        self.mode = mode
        self.waypoint_assigner = self._select_waypoint_assigner()
        
        # Waypoints and schedules
        self.waypoints = predefined_waypoints
        self.schedule = schedule if schedule else []
        self.detail_schedule = detail_schedule if detail_schedule else []

        # Assign waypoints based on the mode
        self.assign_waypoints()

        
        # Build schedule
        self.build_general_schedule()

        # Build detailed trajectories
        self.detail_schedule = detail_schedule if detail_schedule else self.build_trajectories()

    def _select_waypoint_assigner(self):
        """
        Select the appropriate waypoint assigner based on the mode.
        """
        if self.mode == "automatic":
            return AutoWaypointAssigner()
        elif self.mode == "self_chosen":
            return ManualWaypointAssigner()
        else:
            raise ValueError(f"Invalid mode '{self.mode}'. Must be 'automatic' or 'self_chosen'.")
        
    def assign_waypoints(self):
        """
        Assign waypoints using the provided waypoint assigner and the mode of the person.
        """
        if self.mode == "automatic":
            if len(self.waypoints) == 0:
                self.waypoints = self.waypoint_assigner.assign(self)
        elif self.mode == "self_chosen":
            print(f"Person {self.unique_id} is in 'self_chosen' mode. Please assign waypoints manually.")
            self.waypoints = self.waypoint_assigner.assign(self.waypoints)
        else:
            raise ValueError(f"Invalid mode '{self.mode}' for Person {self.unique_id}. Choose 'automatic' or 'self_chosen'.")

######################## Schedule Settings ######################## 

    ### Without UI ###
    # def build_general_schedule(self):
    #     """
    #     Build a general schedule for the person in `self-chosen` mode.

    #     Allows the user to manually specify the movements (start and end waypoints) and start times.
    #     """
    #     if self.mode != "self_chosen":
    #         raise ValueError(f"Cannot manually build schedule in automatic mode for Person {self.unique_id}.")

    #     print(f"Building custom schedule for Person {self.unique_id}:")
    #     schedule = []
        
    #     while True:
    #         print("\nAvailable waypoints:")
    #         for waypoint, coords in self.waypoints.items():
    #             if coords:
    #                 print(f"  - {waypoint}: {coords}")
            
    #         start_waypoint = input("Enter the start waypoint (or 'done' to finish): ").strip()
    #         if start_waypoint.lower() == "done":
    #             break
    #         if start_waypoint not in self.waypoints or not self.waypoints[start_waypoint]:
    #             print(f"Invalid or unassigned start waypoint '{start_waypoint}'. Try again.")
    #             continue

    #         end_waypoint = input("Enter the end waypoint: ").strip()
    #         if end_waypoint not in self.waypoints or not self.waypoints[end_waypoint]:
    #             print(f"Invalid or unassigned end waypoint '{end_waypoint}'. Try again.")
    #             continue

    #         start_time_str = input("Enter the start time (HH:MM, 24-hour format): ").strip()
    #         try:
    #             start_time = datetime.strptime(start_time_str, "%H:%M").time()
    #         except ValueError:
    #             print("Invalid time format. Use HH:MM (e.g., 08:30). Try again.")
    #             continue

    #         # Add the movement to the schedule
    #         schedule.append({
    #             "start_waypoint": start_waypoint,
    #             "end_waypoint": end_waypoint,
    #             "start_time": start_time
    #         })

    #         print(f"Added movement: {start_waypoint} → {end_waypoint} at {start_time_str}.")

    #     # Store the custom schedule
    #     print("\nCustom schedule complete:")
    #     for movement in schedule:
    #         print(f"  {movement['start_time']}: {movement['start_waypoint']} → {movement['end_waypoint']}")
        
    #     self.schedule = schedule

    ### With UI ### 
    def build_general_schedule(self):
        """
        Save a transferred schedule for the person in `self-chosen` mode after validation.

        :param transferred_schedule: List of movements with start times, start waypoints, and end waypoints.
                                    Example:
                                    [
                                        {"start_time": "08:00", "start_waypoint": "home", "end_waypoint": "park"},
                                        {"start_time": "10:00", "start_waypoint": "park", "end_waypoint": "healthcare"},
                                        {"start_time": "12:00", "start_waypoint": "healthcare", "end_waypoint": "home"},
                                    ]
        """
        if self.schedule: 
            validated_schedule = []
            print(f"Validating transferred schedule for Person {self.unique_id}...")

            for movement in self.schedule:
                start_waypoint = movement.get("start_waypoint")
                end_waypoint = movement.get("end_waypoint")
                start_time_str = movement.get("start_time")

                # Convert start_time to string if it is not already
                if isinstance(start_time_str, time):
                    start_time_str = start_time_str.strftime("%H:%M:%S")
                else:
                    start_time_str = start_time_str
                # Remove seconds from time if present
                if len(start_time_str.split(":")) == 3:
                    start_time_str = ":".join(start_time_str.split(":")[:2])  # Convert HH:MM:SS to HH:MM

                # Validate waypoints
                if start_waypoint not in self.waypoints or not self.waypoints[start_waypoint]:
                    print(f"Invalid or unassigned start waypoint: {start_waypoint}. Skipping movement.")
                    continue

                if end_waypoint not in self.waypoints or not self.waypoints[end_waypoint]:
                    print(f"Invalid or unassigned end waypoint: {end_waypoint}. Skipping movement.")
                    continue

                # Validate start time
                try:
                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                except (ValueError, TypeError):
                    print(f"Invalid time format for movement: {start_time_str}. Use HH:MM format. Skipping movement.")
                    continue

                # Add validated movement to the schedule
                validated_schedule.append({
                    "start_time": start_time,
                    "start_waypoint": start_waypoint,
                    "end_waypoint": end_waypoint,
                })
                print(f"Added movement: {start_waypoint} → {end_waypoint} at {start_time_str}.")

            # Save the validated schedule
            self.schedule = validated_schedule

            print("\nFinal Schedule:")
            for movement in self.schedule:
                print(f"  {movement['start_time']}: {movement['start_waypoint']} → {movement['end_waypoint']}")

            

    def build_trajectories(self):
        """
        Compute and store the trajectory for each movement in the schedule, using only time objects.
        """
        enriched_schedule = []
        for movement in self.schedule:
            start_time = movement["start_time"]

            # Get start and end waypoints
            start_coords = self.waypoints[movement["start_waypoint"]]
            end_coords = self.waypoints[movement["end_waypoint"]]

            # Build trajectory using OSMManager
            trajectory = self.osm_manager.build_trajectory(start_coords, end_coords, self.speed)
            
            # Calculate arrival time as general time
            travel_time = timedelta(seconds=trajectory["travel_time_s"])
            arrival_datetime = datetime.combine(datetime.today(), start_time) + travel_time
            arrival_time = arrival_datetime.time()  # Extract only the time part

            # Enrich the schedule entry with trajectory details
            enriched_schedule.append({
                "start_waypoint": movement["start_waypoint"],
                "end_waypoint": movement["end_waypoint"],
                "start_time": start_time,  
                "route_nodes": trajectory["route_nodes"],
                "distance_m": trajectory["distance_m"],
                "travel_time_s": trajectory["travel_time_s"],
                "arrival_time": arrival_time, 
            })

        return enriched_schedule

    ### Without UI ###
    # def get_position_at_time(self, current_time):
    #     """
    #     Determine the position of the person at a specific time.
    #     :param current_time: A datetime object in the format 'YYYY-MM-DD HH:mm:ss'.
    #     :return: Tuple (latitude, longitude) representing the person's position.
    #     """
    #     # Extract the time component from the provided datetime
    #     current_time_only = current_time.time()
    #     print(f"Checking position at time: {current_time_only}")

    #     for i, movement in enumerate(self.detail_schedule):
    #         start_time = movement["start_time"]
    #         arrival_time = movement["arrival_time"]
    #         print(f"Movement {i}: {movement['start_waypoint']} → {movement['end_waypoint']}")
    #         print(f"    Start time: {start_time}, Arrival time: {arrival_time}")

    #         if start_time <= current_time_only <= arrival_time:
    #             # Calculate the person's position if they are traveling
    #             elapsed_time_s = (
    #                 datetime.combine(datetime.today(), current_time_only) -
    #                 datetime.combine(datetime.today(), start_time)
    #             ).total_seconds()
    #             fraction_traveled = elapsed_time_s / movement["travel_time_s"]

    #             print(f"    Elapsed time: {elapsed_time_s} seconds")
    #             print(f"    Fraction of route traveled: {fraction_traveled:.2f}")

    #             # Interpolate position along the route
    #             interpolated_position = self.interpolate_position(
    #                 movement["route_nodes"], fraction_traveled, movement["distance_m"]
    #             )

    #             interpolated_position = (float(interpolated_position[0]), float(interpolated_position[1]))
    #             print(f"    Interpolated position: {interpolated_position}")
    #             return interpolated_position

    #         elif current_time_only < start_time:
    #             # The person hasn't started this movement yet; return the previous waypoint
    #             print(f"    Current time is before this movement. Returning start waypoint: {movement['start_waypoint']}")
    #             return self.waypoints[movement["start_waypoint"]]

    #     # If the current time is after all movements, return the final destination
    #     final_position = self.waypoints[self.detail_schedule[-1]["end_waypoint"]]
    #     print(f"All movements completed. Returning final position: {final_position}")
    #     return final_position

    ### With UI ###
    def get_position_at_time(self, current_time):
        """
        Determine the position of the person at a specific time and generate a log.
        :param current_time: A datetime object in the format 'YYYY-MM-DD HH:mm:ss'.
        :return: Tuple containing:
            - (latitude, longitude) representing the person's position.
            - Detailed log string.
        """
        current_time_only = current_time.time()
        log = f"Checking position at time: {current_time_only} \n"
        print(f"Checking position at time: {current_time_only}")

        for i, movement in enumerate(self.detail_schedule):
            start_time = movement["start_time"]
            arrival_time = movement["arrival_time"]
            log += f"Movement {i}: {movement['start_waypoint']} → {movement['end_waypoint']} \n"
            log += f"    Start time: {start_time}, Arrival time: {arrival_time} \n"
            print(f"Movement {i}: {movement['start_waypoint']} → {movement['end_waypoint']}")
            print(f"    Start time: {start_time}, Arrival time: {arrival_time}")

            if start_time <= current_time_only <= arrival_time:
                elapsed_time_s = (
                    datetime.combine(datetime.today(), current_time_only) -
                    datetime.combine(datetime.today(), start_time)
                ).total_seconds()
                fraction_traveled = elapsed_time_s / movement["travel_time_s"]

                log += f"    Elapsed time: {elapsed_time_s} seconds\n"
                log += f"    Fraction of route traveled: {fraction_traveled:.2f} \n"
                print(f"    Elapsed time: {elapsed_time_s} seconds")
                print(f"    Fraction of route traveled: {fraction_traveled:.2f}")

                interpolated_position = self.interpolate_position(
                    movement["route_nodes"], fraction_traveled, movement["distance_m"]
                )
                interpolated_position = (float(interpolated_position[0]), float(interpolated_position[1]))
                log += f"    Interpolated position: {interpolated_position}\n"
                print(f"    Interpolated position: {interpolated_position}")
                return interpolated_position, log

            elif current_time_only < start_time:
                log += f"    Current time is before this movement. Returning start waypoint: {movement['start_waypoint']} \n"
                print(f"    Current time is before this movement. Returning start waypoint: {movement['start_waypoint']}")
                
                return self.waypoints[movement["start_waypoint"]], log

        final_position = self.waypoints[self.detail_schedule[-1]["end_waypoint"]]
        log += f"All movements completed. Returning final position: {final_position} \n"
        print(f"All movements completed. Returning final position: {final_position}")

        return final_position, log
    
    def interpolate_position(self, route_nodes, fraction, total_distance):
        """
        Interpolate the position along the route using straight-line distance between nodes.
        :param route_nodes: List of node IDs representing the route.
        :param fraction: Fraction of the route completed (0 to 1).
        :param total_distance: Precomputed total distance of the route in meters.
        :return: Tuple (latitude, longitude) representing the interpolated position.
        """
        target_distance = fraction * total_distance

        cumulative_distance = 0
        for i in range(len(route_nodes) - 1):
            node_a, node_b = route_nodes[i], route_nodes[i + 1]

            # Get coordinates of the nodes
            coords_a = (self.osm_manager.nodes.loc[node_a, "y"], self.osm_manager.nodes.loc[node_a, "x"])
            coords_b = (self.osm_manager.nodes.loc[node_b, "y"], self.osm_manager.nodes.loc[node_b, "x"])

            # Calculate the straight-line distance between the nodes
            segment_distance = self.osm_manager.straight_line_distance(coords_a, coords_b)

            if cumulative_distance + segment_distance >= target_distance:
                # Interpolate between node_a and node_b
                remaining_distance = target_distance - cumulative_distance
                interpolation_fraction = remaining_distance / segment_distance

                lat = coords_a[0] + (coords_b[0] - coords_a[0]) * interpolation_fraction
                lon = coords_a[1] + (coords_b[1] - coords_a[1]) * interpolation_fraction
                return lat, lon

            cumulative_distance += segment_distance

        # Fallback: Return the last node's coordinates
        last_node = route_nodes[-1]
        return (
            self.osm_manager.nodes.loc[last_node, "y"],
            self.osm_manager.nodes.loc[last_node, "x"]
        )
    

######################## Serialization and Deserialization ######################## 

    def to_dict(self):
        """Serialize the Person object to a dictionary."""
        return {
            "unique_id": self.unique_id,
            "type": self.type,
            "speed": self.speed,
            "mode": self.mode,
            "waypoints": self.waypoints,
            "schedule": [
                {
                    "start_waypoint": movement["start_waypoint"],
                    "end_waypoint": movement["end_waypoint"],
                    "start_time": movement["start_time"].strftime("%H:%M:%S")
                }
                for movement in self.schedule
            ],
            "detail_schedule": [
                {
                    "start_waypoint": movement["start_waypoint"],
                    "end_waypoint": movement["end_waypoint"],
                    "start_time": movement["start_time"].strftime("%H:%M:%S"),
                    "route_nodes": movement["route_nodes"],
                    "distance_m": movement["distance_m"],
                    "travel_time_s": movement["travel_time_s"],
                    "arrival_time": movement["arrival_time"].strftime("%H:%M:%S"),
                }
                for movement in self.detail_schedule
            ],
        }

    @classmethod
    def from_dict(cls, data, osm_manager):
        """
        Deserialize a dictionary to a Person object.

        :param data: A dictionary representing a serialized Person object.
        :param osm_manager: An OSMManager instance for geographic and route data.
        :return: A deserialized Person object (or its subclass).
        """

        # Create an instance with basic fields
        instance = cls(
            unique_id=data["unique_id"],
            person_type=data["type"],
            speed=data["speed"],
            osm_manager=osm_manager,
            predefined_waypoints = data["waypoints"],
            schedule=[
                {
                    "start_waypoint": movement["start_waypoint"],
                    "end_waypoint": movement["end_waypoint"],
                    "start_time": datetime.strptime(movement["start_time"], "%H:%M:%S").time(),
                }
                for movement in data["schedule"]
            ],
            detail_schedule=[
                {
                    "start_waypoint": movement["start_waypoint"],
                    "end_waypoint": movement["end_waypoint"],
                    "start_time": datetime.strptime(movement["start_time"], "%H:%M:%S").time(),
                    "route_nodes": movement["route_nodes"],  # Already serializable
                    "distance_m": movement["distance_m"],
                    "travel_time_s": movement["travel_time_s"],
                    "arrival_time": datetime.strptime(movement["arrival_time"], "%H:%M:%S").time(),
                }
                for movement in data["detail_schedule"]
            ],
            mode=data["mode"],
        )

        return instance