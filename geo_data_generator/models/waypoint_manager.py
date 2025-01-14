from abc import ABC, abstractmethod
import random
from shapely.geometry import Point, Polygon, MultiPolygon

class WaypointAssigner(ABC):
    @abstractmethod
    def assign(self, person):
        pass

class AutoWaypointAssigner(WaypointAssigner):
    def assign(self, person):
        """
        Assign waypoints automatically based on the person's type.
        """
        waypoint_methods = {
            "child": self._assign_child_waypoints,
            "adult": self._assign_adult_waypoints,
            "older": self._assign_older_waypoints,
        }

        if person.type not in waypoint_methods:
            raise ValueError(f"Unknown person type: {person.type}")

        # Assign waypoints based on type
        waypoints = waypoint_methods[person.type](person)
        
        # Update person's waypoints
        person.waypoints.update(waypoints)
        
        return person.waypoints

    def _assign_child_waypoints(self, person):
        return self._assign_multiple_locations(person, {
            "home": {"category": "residential"},
            "school": {"category": "schools", "nearest_to": "home"},
            "park": {"category": "parks"},
        })

    def _assign_adult_waypoints(self, person):
        return self._assign_multiple_locations(person, {
            "home": {"category": "residential"},
            "workplace": {"category": "workplaces"},
            "gym": {"category": "gyms", "nearest_to": "home"},
            "market": {"category": "markets", "nearest_to": "home"},
        })

    def _assign_older_waypoints(self, person):
        return self._assign_multiple_locations(person, {
            "home": {"category": "residential"},
            "healthcare": {"category": "healthcare", "nearest_to": "home"},
            "park": {"category": "parks", "nearest_to": "home"},
        })

    def _assign_multiple_locations(self, person, location_config):
        """
        Assign multiple waypoints based on the configuration.
        
        :param person: The Person object.
        :param location_config: A dictionary where keys are waypoint types and values are
                                configurations containing 'category' and optionally 'nearest_to'.
        :return: A dictionary of assigned waypoints.
        """
        assigned_waypoints = {}

        for waypoint, config in location_config.items():
            category = config["category"]
            nearest_to = config.get("nearest_to")

            # If nearest_to is specified, assign based on proximity
            if nearest_to:
                if nearest_to not in assigned_waypoints and not person.waypoints.get(nearest_to):
                    raise ValueError(f"Waypoint '{nearest_to}' must be assigned before '{waypoint}'.")
                reference_point = assigned_waypoints.get(nearest_to) or person.waypoints[nearest_to]
                assigned_waypoints[waypoint] = self._assign_location(category, person, nearest_to_point=reference_point)
            else:
                # Regular assignment
                assigned_waypoints[waypoint] = self._assign_location(category, person)

        return assigned_waypoints

    def _assign_location(self, category, person, nearest_to_point=None):
        """
        Assign a location based on the category, optionally finding the nearest to a given point.
        
        :param category: The category of the location (e.g., 'residential', 'parks').
        :param person: The Person object.
        :param nearest_to_point: A tuple (latitude, longitude) to find the nearest location.
        :return: The assigned location as a tuple (latitude, longitude).
        """
        areas = person.osm_manager.locations.get(category)

        if areas is None or areas.empty:
            print(f"No {category} areas found for Person {person.unique_id}. Falling back to bounding box.")
            return self._random_point_in_bbox(person)

        if nearest_to_point:
            reference_point = Point(nearest_to_point[1], nearest_to_point[0])
            nearest_geom = min(
                areas.geometry,
                key=lambda geom: reference_point.distance(geom.centroid)
            )
            return (nearest_geom.centroid.y, nearest_geom.centroid.x)
        else:
            polygon = self._choose_random_polygon(areas)
            return self._random_point_in_polygon(polygon) if polygon else self._random_point_in_bbox(person)
        
    def _random_point_in_bbox(self, person):
        """
        Assign a random point within the bounding box of the graph.
        """
        bounds = person.osm_manager.graph.graph.get("bbox")
        if not bounds:
            raise ValueError(f"No bounding box available for Person {person.unique_id}.")
        min_x, min_y, max_x, max_y = bounds

        random_point = Point(
            random.uniform(min_x, max_x),
            random.uniform(min_y, max_y)
        )
        return (random_point.y, random_point.x)

    def _choose_random_polygon(self, geodataframe):
        """
        Safely choose a random Polygon or MultiPolygon from a GeoDataFrame.
        """
        polygons = [
            geom for geom in geodataframe.geometry
            if isinstance(geom, (Polygon, MultiPolygon))
        ]
        return random.choice(polygons) if polygons else None

    def _random_point_in_polygon(self, polygon, max_attempts=1000):
        """
        Generate a random point within a given Polygon or MultiPolygon.
        """
        min_x, min_y, max_x, max_y = polygon.bounds

        for _ in range(max_attempts):
            random_point = Point(
                random.uniform(min_x, max_x),
                random.uniform(min_y, max_y)
            )
            if polygon.contains(random_point):
                return (random_point.y, random_point.x)

        print(f"Warning: Unable to find a random point in polygon after {max_attempts} attempts.")
        return None
    
class ManualWaypointAssigner(WaypointAssigner):

    ### Without UI ###
    # def assign(self, person):
    #     """
    #     Allow the user to manually select which waypoints to assign based on the person type.
    #     """
    #     waypoints = {}
    #     waypoint_options = self._get_waypoints_for_person_type(person.type)

    #     print(f"Manually assigning waypoints for Person {person.unique_id} (Type: {person.type})")
    #     for waypoint_type in waypoint_options:
    #         waypoints[waypoint_type] = self._get_user_input_for_waypoint(waypoint_type)

    #     print("\nSummary of manually assigned waypoints:")
    #     for waypoint, coords in waypoints.items():
    #         if coords:
    #             print(f"  {waypoint}: {coords}")
    #         else:
    #             print(f"  {waypoint}: Not assigned.")
    #     return waypoints

    # def _get_waypoints_for_person_type(self, person_type):
    #     """
    #     Determine applicable waypoints for a given person type.
    #     """
    #     person_waypoints = {
    #         "child": ["home", "school", "park"],
    #         "adult": ["home", "workplace", "gym", "market"],
    #         "older": ["home", "healthcare", "park"],
    #     }
    #     if person_type not in person_waypoints:
    #         raise ValueError(f"Unknown person type: {person_type}")
    #     return person_waypoints[person_type]

    # def _get_user_input_for_waypoint(self, waypoint_type):
    #     """
    #     Prompt the user for manual input to assign a waypoint.
    #     """
    #     user_input = input(f"Do you want to assign a location for {waypoint_type}? (yes/no): ").strip().lower()
    #     if user_input != "yes":
    #         return None

    #     try:
    #         lat = float(input(f"Enter latitude for {waypoint_type} (between -90 and 90): "))
    #         lon = float(input(f"Enter longitude for {waypoint_type} (between -180 and 180): "))
    #         return lat, lon
    #     except ValueError:
    #         print(f"Invalid coordinates provided for {waypoint_type}. Skipping.")
    #         return None

    ### With UI ###
    def assign(self, predefined_waypoints):
        """
        Assign waypoints using a predefined set of coordinates.

        :param predefined_waypoints: Dictionary of waypoints to validate and assign.
                                     Example: {"home": (12.34, 56.78), "school": (98.76, 54.32)}
        :return: Dictionary of validated waypoints.
        """
        waypoints = {}
        print("Validating predefined waypoints...")

        for waypoint, coords in predefined_waypoints.items():
            if self._is_valid_coordinates(coords):
                waypoints[waypoint] = coords
                print(f"Assigned {waypoint} at {coords}.")
            else:
                print(f"Invalid coordinates for {waypoint}: {coords}. Skipping.")

        print("\nSummary of assigned waypoints:")
        for waypoint, coords in waypoints.items():
            print(f"  {waypoint}: {coords if coords else 'Not assigned'}")

        return waypoints

    def _is_valid_coordinates(self, coords):
        """
        Check if the provided coordinates are valid.

        :param coords: Tuple of (latitude, longitude).
        :return: True if valid, False otherwise.
        """
        if not isinstance(coords, (tuple, list)) or len(coords) != 2:
            return False

        lat, lon = coords
        return -90 <= lat <= 90 and -180 <= lon <= 180