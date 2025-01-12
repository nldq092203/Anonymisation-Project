import random
from shapely.geometry import Point, Polygon, MultiPolygon
from datetime import datetime, timedelta

class Person:
    def __init__(self, unique_id, type, speed, osm_manager):
        """
        A Person in the simulation with assigned waypoints such as home, workplace, etc.
        
        :param unique_id: Unique identifier for the person
        :param type: 'child', 'adult', or 'older'
        :param speed: Speed of movement (units can vary based on your simulation)
        :param osm_manager: An OSMManager-like object holding relevant location data
        """
        self.osm_manager = osm_manager
        self.unique_id = unique_id
        self.type = type
        self.speed = speed

        # Dictionary to store the person's assigned waypoints
        self.waypoints = {
            "home": None,
            "school": None,
            "workplace": None,
            "park": None,
            "market": None,
            "healthcare": None,
            "play_area": None,
            "gym": None
        }

        # Assign the waypoints based on the person's type
        self.assign_waypoints()
        
        self.schedule = self.build_general_schedule()
        self.detail_schedule = self.build_trajectories()

    def assign_waypoints(self):
        """
        Base method to assign waypoints. Subclasses override this to assign specific waypoints.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def assign_home(self):
        """
        Assign a home location within a residential area or fallback to a random
        bounding-box location if no residential areas are found.
        :return: A tuple (latitude, longitude) representing the assigned home.
        """
        residential_areas = self.osm_manager.locations.get("residential")

        # If no residential areas are found, fallback to bounding box
        if residential_areas is None or residential_areas.empty:
            print(f"No residential areas found for Person {self.unique_id}.")
            home_coords = self._random_point_in_bbox()
        else:
            # Randomly select a residential polygon/multipolygon
            residential_polygon = self._choose_random_polygon(residential_areas)
            if residential_polygon is None:
                print(f"No valid polygons found in residential areas for Person {self.unique_id}.")
                home_coords = self._random_point_in_bbox()
            else:
                home_coords = self.get_random_point_in_polygon(residential_polygon)

        self.waypoints["home"] = home_coords
        print(f"Person {self.unique_id} assigned home at {self.waypoints['home']}.")
        return self.waypoints["home"]

    def assign_workplace(self):
        """
        Assign a workplace location within the available workplace areas or 
        fallback to a random bounding-box location if none found.
        :return: A tuple (latitude, longitude) representing the assigned workplace.
        """
        workplace_areas = self.osm_manager.locations.get("workplaces")

        if workplace_areas is None or workplace_areas.empty:
            print(f"No workplaces found for Person {self.unique_id}.")
            workplace_coords = self._random_point_in_bbox()
        else:
            workplace_polygon = self._choose_random_polygon(workplace_areas)
            if workplace_polygon is None:
                print(f"No valid polygons found in workplace areas for Person {self.unique_id}.")
                workplace_coords = self._random_point_in_bbox()
            else:
                workplace_coords = self.get_random_point_in_polygon(workplace_polygon)

        self.waypoints["workplace"] = workplace_coords
        print(f"Person {self.unique_id} assigned workplace at {self.waypoints['workplace']}.")
        return self.waypoints["workplace"]

    def assign_school(self):
        """
        Assign the closest school to the person's home, or fallback if none found.
        :return: A tuple (latitude, longitude) representing the assigned school.
        """
        if not self.waypoints["home"]:
            raise ValueError(f"Home is not assigned for Person {self.unique_id}. Assign home first.")

        school_areas = self.osm_manager.locations.get("schools")

        if school_areas is None or school_areas.empty:
            print(f"No schools found for Person {self.unique_id}.")
            school_coords = self._random_point_in_bbox()
        else:
            home_point = Point(self.waypoints["home"][1], self.waypoints["home"][0])
            # Pick the geometry with the smallest distance to home
            nearest_school_geom = min(
                school_areas.geometry,
                key=lambda geom: home_point.distance(geom.centroid)
            )
            school_coords = (nearest_school_geom.centroid.y, nearest_school_geom.centroid.x)

        self.waypoints["school"] = school_coords
        print(f"Person {self.unique_id} assigned school at {self.waypoints['school']}.")
        return self.waypoints["school"]

    def assign_park(self):
        """
        Assign the closest park to the person's home, or fallback if none found.
        :return: A tuple (latitude, longitude) representing the assigned park.
        """
        if not self.waypoints["home"]:
            raise ValueError(f"Home is not assigned for Person {self.unique_id}. Assign home first.")

        park_areas = self.osm_manager.locations.get("parks")

        if park_areas is None or park_areas.empty:
            print(f"No parks found for Person {self.unique_id}.")
            park_coords = self._random_point_in_bbox()
        else:
            home_point = Point(self.waypoints["home"][1], self.waypoints["home"][0])
            nearest_park_geom = min(
                park_areas.geometry,
                key=lambda geom: home_point.distance(geom.centroid)
            )
            park_coords = (nearest_park_geom.centroid.y, nearest_park_geom.centroid.x)

        self.waypoints["park"] = park_coords
        print(f"Person {self.unique_id} assigned park at {self.waypoints['park']}.")
        return self.waypoints["park"]

    def assign_market(self):
        """
        Assign the closest market to the person's home, or fallback if none found.
        :return: A tuple (latitude, longitude) representing the assigned market.
        """
        if not self.waypoints["home"]:
            raise ValueError(f"Home is not assigned for Person {self.unique_id}. Assign home first.")

        market_areas = self.osm_manager.locations.get("markets")

        if market_areas is None or market_areas.empty:
            print(f"No markets found for Person {self.unique_id}.")
            market_coords = self._random_point_in_bbox()
        else:
            home_point = Point(self.waypoints["home"][1], self.waypoints["home"][0])
            nearest_market_geom = min(
                market_areas.geometry,
                key=lambda geom: home_point.distance(geom.centroid)
            )
            market_coords = (nearest_market_geom.centroid.y, nearest_market_geom.centroid.x)

        self.waypoints["market"] = market_coords
        print(f"Person {self.unique_id} assigned market at {self.waypoints['market']}.")
        return self.waypoints["market"]

    def assign_healthcare(self):
        """
        Assign the closest healthcare facility to the person's home, or fallback if none found.
        :return: A tuple (latitude, longitude) representing the assigned healthcare facility.
        """
        if not self.waypoints["home"]:
            raise ValueError(f"Home is not assigned for Person {self.unique_id}. Assign home first.")

        healthcare_areas = self.osm_manager.locations.get("healthcare")

        if healthcare_areas is None or healthcare_areas.empty:
            print(f"No healthcare facilities found for Person {self.unique_id}.")
            healthcare_coords = self._random_point_in_bbox()
        else:
            home_point = Point(self.waypoints["home"][1], self.waypoints["home"][0])
            nearest_healthcare_geom = min(
                healthcare_areas.geometry,
                key=lambda geom: home_point.distance(geom.centroid)
            )
            healthcare_coords = (nearest_healthcare_geom.centroid.y, nearest_healthcare_geom.centroid.x)

        self.waypoints["healthcare"] = healthcare_coords
        print(f"Person {self.unique_id} assigned healthcare at {self.waypoints['healthcare']}.")
        return self.waypoints["healthcare"]

    def assign_play_area(self):
        """
        Assign a play area location within the available play area polygons 
        or fallback to a random bounding-box location.
        :return: A tuple (latitude, longitude) representing the assigned play area.
        """
        play_area_locations = self.osm_manager.locations.get("play_areas")

        if play_area_locations is None or play_area_locations.empty:
            print(f"No play areas found for Person {self.unique_id}.")
            play_coords = self._random_point_in_bbox()
        else:
            play_polygon = self._choose_random_polygon(play_area_locations)
            if play_polygon is None:
                print(f"No valid polygons found in play areas for Person {self.unique_id}.")
                play_coords = self._random_point_in_bbox()
            else:
                play_coords = self.get_random_point_in_polygon(play_polygon)

        self.waypoints["play_area"] = play_coords
        print(f"Person {self.unique_id} assigned play area at {self.waypoints['play_area']}.")
        return self.waypoints["play_area"]

    def assign_gym(self):
        """
        Assign the closest gym to the person's home, or fallback if none found.
        :return: A tuple (latitude, longitude) representing the assigned gym.
        """
        if not self.waypoints["home"]:
            raise ValueError(f"Home is not assigned for Person {self.unique_id}. Assign home first.")

        gym_areas = self.osm_manager.locations.get("gyms")

        if gym_areas is None or gym_areas.empty:
            print(f"No gyms found for Person {self.unique_id}.")
            gym_coords = self._random_point_in_bbox()
        else:
            home_point = Point(self.waypoints["home"][1], self.waypoints["home"][0])
            nearest_gym_geom = min(
                gym_areas.geometry,
                key=lambda geom: home_point.distance(geom.centroid)
            )
            gym_coords = (nearest_gym_geom.centroid.y, nearest_gym_geom.centroid.x)

        self.waypoints["gym"] = gym_coords
        print(f"Person {self.unique_id} assigned gym at {self.waypoints['gym']}.")
        return self.waypoints["gym"]

    def get_random_point_in_polygon(self, polygon, max_attempts=1000):
        """
        Generate a random point within a given Polygon or MultiPolygon.
        
        :param polygon: Shapely Polygon or MultiPolygon geometry.
        :param max_attempts: Safety limit to prevent infinite loops in edge cases.
        :return: A tuple (latitude, longitude) representing the random point.
        """
        min_x, min_y, max_x, max_y = polygon.bounds

        for _ in range(max_attempts):
            random_point = Point(
                random.uniform(min_x, max_x),
                random.uniform(min_y, max_y)
            )
            if polygon.contains(random_point):
                return (random_point.y, random_point.x)

        # If no point found within max_attempts, fallback to bounding-box approach
        print(f"Warning: Unable to find a random point inside polygon within {max_attempts} attempts.")
        return self._random_point_in_bbox()

    def _random_point_in_bbox(self):
        """
        Assign a random point within the bounding box of the graph if available.
        :return: A tuple (latitude, longitude) for the random location or None if not available.
        """
        bounds = self.osm_manager.graph.graph.get("bbox")
        if not bounds:
            print(f"No bounding box available. Cannot assign location for Person {self.unique_id}.")
            return None
        min_x, min_y, max_x, max_y = bounds

        random_point = Point(
            random.uniform(min_x, max_x),
            random.uniform(min_y, max_y)
        )
        return (random_point.y, random_point.x)

    def _choose_random_polygon(self, geodataframe):
        """
        Safely choose a random Polygon or MultiPolygon from a GeoDataFrame.
        
        :param geodataframe: A GeoDataFrame containing geometries.
        :return: A Polygon or MultiPolygon, or None if none are valid.
        """
        polygons = [
            geom for geom in geodataframe.geometry
            if isinstance(geom, (Polygon, MultiPolygon))
        ]
        if not polygons:
            return None
        return random.choice(polygons)

######################## Schedule Settings ######################## 

    def build_general_schedule(self):
        """
        Base method to build a schedule. Subclasses override this to define specific schedules.
        """
        raise NotImplementedError("Subclasses must implement this method.")


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


    def get_position_at_time(self, current_time):
        """
        Determine the position of the person at a specific time.
        :param current_time: A datetime object in the format 'YYYY-MM-DD HH:mm:ss'.
        :return: Tuple (latitude, longitude) representing the person's position.
        """
        # Extract the time component from the provided datetime
        current_time_only = current_time.time()

        for movement in self.detail_schedule:
            start_time = movement["start_time"]
            arrival_time = movement["arrival_time"]

            if start_time <= current_time_only <= arrival_time:
                # Calculate the person's position if they are traveling
                elapsed_time_s = (
                    datetime.combine(datetime.today(), current_time_only) -
                    datetime.combine(datetime.today(), start_time)
                ).total_seconds()
                fraction_traveled = elapsed_time_s / movement["travel_time_s"]

                # Interpolate position along the route
                return self.interpolate_position(
                    movement["route_nodes"], fraction_traveled, movement["distance_m"]
                )

            elif current_time_only < start_time:
                # The person hasn't started this movement yet; return the previous waypoint
                return self.waypoints[movement["start_waypoint"]]

        # If the current time is after all movements, return the final destination
        return self.waypoints[self.detail_schedule[-1]["end_waypoint"]]
    
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