import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
import geopandas as gpd
import os
import pickle
import hashlib
class OSMManager:
    def __init__(self, center_point, radius=10000, network_type="drive", cache_dir="graph_cache"):
        """
        Initialize the OSMManager with a graph for a specified center point and radius.
        :param center_point: (latitude, longitude) of the center point.
        :param radius: Radius in meters for the area of interest.
        :param network_type: Type of network to load (default: 'drive').
        """
        self.center_point = center_point
        self.radius = radius
        self.network_type = network_type

        self.cache_dir = cache_dir

        # Ensure the cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)

        # Initialize attributes to store data
        self.graph = None
        self.nodes = None
        self.edges = None
        self.locations = {
            "schools": None,
            "workplaces": None,
            "parks": None,
            "markets": None,
            "healthcare": None,
            "play_areas": None,
            "gyms": None,
            "residential": None
        }

        # Load the graph
        self.load_graph()


        # Scan all locations
        self.scan_all_locations()

    def _generate_cache_key(self):
        """
        Generate a unique cache key for the current center point and radius.
        :return: A unique hash string.
        """
        key_data = f"{self.center_point}-{self.radius}-{self.network_type}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def load_graph(self):
        """
        Load the graph for the specified center point and radius.
        Reuse cached graph if available.
        """
        cache_key = self._generate_cache_key()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        if os.path.exists(cache_path):
            print(f"Loading graph from cache: {cache_path}")
            with open(cache_path, "rb") as f:
                self.graph = pickle.load(f)
        else:
            print(f"Generating graph for center point {self.center_point} with radius {self.radius} meters...")
            self.graph = ox.graph_from_point(
                self.center_point, dist=self.radius, network_type=self.network_type, simplify=True
            )
            with open(cache_path, "wb") as f:
                pickle.dump(self.graph, f)
            print(f"Graph saved to cache: {cache_path}")

        # Convert the graph to GeoDataFrames
        self.nodes, self.edges = ox.graph_to_gdfs(self.graph)

    def get_nearest_node(self, point):
        """
        Find the nearest node to a given point.
        :param point: (latitude, longitude)
        :return: Node ID
        """
        return ox.nearest_nodes(self.graph, X=point[1], Y=point[0])

    def shortest_path(self, origin_point, destination_point, weight="length"):
        """
        Calculate the shortest path between two points.
        :param origin_point: (latitude, longitude) of the origin.
        :param destination_point: (latitude, longitude) of the destination.
        :param weight: Edge weight to optimize (default: 'length').
        :return: List of node IDs representing the shortest path.
        Dijkstra’s Algorithm
        """
        origin_node = self.get_nearest_node(origin_point)
        destination_node = self.get_nearest_node(destination_point)
        route = nx.shortest_path(self.graph, origin_node, destination_node, weight=weight)
        return route

    def route_distance(self, route):
        """
        Calculate the total distance of a route.
        :param route: List of node IDs representing a path.
        :return: Total distance in meters.
        """
        return sum(nx.get_edge_attributes(self.graph, "length")[(route[i], route[i + 1], 0)]
                   for i in range(len(route) - 1))
    
    def straight_line_distance(self, point1, point2):
            """
            Calculate the straight-line distance between two points.
            :param point1: (latitude, longitude) of the first point.
            :param point2: (latitude, longitude) of the second point.
            :return: Distance in meters.
            """
            return geodesic(point1, point2).meters

    def scan_locations(self, category, tags):
        """
        General method to scan locations for a given category using tags.
        :param category: The category of the location (e.g., 'parks', 'schools').
        :param tags: Dictionary of OSM tags for filtering locations.
        :return: GeoDataFrame containing the scanned locations.
        """
        print(f"Scanning for {category} near {self.center_point} within {self.radius} meters...")
        try:
            locations = ox.features_from_point(self.center_point, dist=self.radius, tags=tags)
        except Exception as e:
            print(f"Error scanning {category}: {e}")
            locations = gpd.GeoDataFrame()
        self.locations[category] = locations
        if not locations.empty:
            print(f"Found {len(locations)} {category}.")
        else:
            print(f"No {category} found in the specified area.")
        return locations

    # def scan_residentals(self):
    #     """
    #     Scan for residential areas using the generalized scan_locations method.
    #     :return: GeoDataFrame containing residential areas.
    #     """
    #     # Define OSM tags for residential areas
    #     tags = {"landuse": "residential"}

    #     return self.scan_locations("residential", tags)
    
    # def scan_parks(self):
    #     return self.scan_locations("parks", {"leisure": "park"})

    # def scan_schools(self):
    #     return self.scan_locations("schools", {"amenity": "school"})

    # def scan_workplaces(self):
    #     return self.scan_locations("workplaces", {"office": True, "industrial": True})

    # def scan_markets(self):
    #     return self.scan_locations("markets", {"shop": "supermarket"})

    # def scan_healthcare(self):
    #     return self.scan_locations("healthcare", {"amenity": ["hospital", "clinic", "pharmacy"]})

    # def scan_play_areas(self):
    #     return self.scan_locations("play_areas", {"leisure": "playground"})

    # def scan_gyms(self):
    #     return self.scan_locations("gyms", {"leisure": "fitness_centre"})

    def scan_all_locations(self):
        """Scan and store locations for all predefined categories."""
        categories = {
            "residential": {"landuse": "residential"},
            "parks": {"leisure": "park"},
            "schools": {"amenity": "school"},
            "workplaces": {"office": True, "landuse": "industrial"},
            "markets": {"shop": "supermarket"},
            "healthcare": {"amenity": ["hospital", "clinic", "pharmacy"]},
            "play_areas": {"leisure": "playground"},
            "gyms": {"leisure": "fitness_centre"}
        }
        for category, tags in categories.items():
            print(f"Scanning for {category}...")
            self.locations[category] = self.scan_locations(category, tags)


    def build_trajectory(self, depart, arrival, speed_m_s=1.4):
        """
        Build the trajectory (with details) between two points.
        :param depart: Tuple (latitude, longitude) of the departure point.
        :param arrival: Tuple (latitude, longitude) of the arrival point.
        :param speed_m_s: Average speed in meters/second (default: 1.4 m/s for walking).
        :return: Dictionary containing trajectory details.
        """
        try:
            # Get the nearest nodes for departure and arrival points
            depart_node = self.get_nearest_node(depart)
            arrival_node = self.get_nearest_node(arrival)
            print(f"Depart Node: {depart_node}, Arrival_node: {arrival_node}")

            # Try finding the shortest path directly
            try:
                route_nodes = nx.shortest_path(self.graph, depart_node, arrival_node, weight="length")
            except nx.NetworkXNoPath:
                # Handle the case where no direct path exists
                route_nodes, depart_node, arrival_node = self._handle_no_path(depart, arrival, depart_node, arrival_node)
                if not route_nodes:
                    return self._straight_line_fallback(depart_node , arrival_node, speed_m_s)

            # Calculate the total distance of the route
            distance_m = self.route_distance(route_nodes)

            # Calculate travel time in seconds
            travel_time_s = distance_m / speed_m_s

            # Build the detailed trajectory information
            trajectory_details = {
                "start_waypoint": depart,
                "end_waypoint": arrival,
                "route_nodes": route_nodes,
                "distance_m": distance_m,
                "travel_time_s": travel_time_s,
            }

            print(f"Trajectory built from {depart} to {arrival} with {len(route_nodes)} nodes.")
            return trajectory_details

        except Exception as e:
            print(f"Unexpected error building trajectory from {depart} to {arrival}: {e}")
            # Fallback to straight line in case of any unexpected error
            return self._straight_line_fallback(depart, arrival, speed_m_s)

    def _handle_no_path(self, depart, arrival, depart_node, arrival_node):
        """
        Handle cases where no direct path exists between two nodes by expanding search space.
        :param depart: Departure coordinates (latitude, longitude).
        :param arrival: Arrival coordinates (latitude, longitude).
        :param depart_node: Closest graph node to the departure point.
        :param arrival_node: Closest graph node to the arrival point.
        :return: Tuple (route_nodes, updated_depart_node, updated_arrival_node).
        """
        nearby_depart_nodes = self.get_nearby_nodes(depart_node)
        nearby_arrival_nodes = self.get_nearby_nodes(arrival_node)
        print(f"Nearby_depart_node: {nearby_depart_nodes}, Nearby_arrival_nodes: {nearby_arrival_nodes}")

        # Try finding a path using nearby nodes
        for d_node in nearby_depart_nodes:
            for a_node in nearby_arrival_nodes:
                try:
                    route_nodes = nx.shortest_path(self.graph, d_node, a_node, weight="length")
                    print(f"Path found between nearby nodes: {d_node} → {a_node}")
                    return route_nodes, d_node, a_node
                except nx.NetworkXNoPath:
                    continue

        # If no path found, return None
        print(f"No path found between nearby nodes for {depart} to {arrival}.")
        return None, None, None

    def _straight_line_fallback(self, start, end, speed_m_s):
        """
        Fallback to a straight-line trajectory if no valid path exists.
        :param start: Can be a tuple (latitude, longitude) or a node ID.
        :param end: Can be a tuple (latitude, longitude) or a node ID.
        :param speed_m_s: Average speed in meters/second.
        :return: Dictionary containing fallback trajectory details.
        """
        # Resolve node IDs to coordinates if necessary
        if isinstance(start, (int, str)):  # Node ID
            start_coords = (self.osm_manager.nodes.loc[start, "y"], self.osm_manager.nodes.loc[start, "x"])
        else:
            start_coords = start  # Already a coordinate

        if isinstance(end, (int, str)):  # Node ID
            end_coords = (self.osm_manager.nodes.loc[end, "y"], self.osm_manager.nodes.loc[end, "x"])
        else:
            end_coords = end  # Already a coordinate

        distance_m = self.straight_line_distance(start_coords, end_coords)
        travel_time_s = distance_m / speed_m_s

        print(f"Fallback: Using straight line from {start_coords} to {end_coords}.")
        return {
            "start_waypoint": start_coords,
            "end_waypoint": end_coords,
            "route_nodes": [start_coords, end_coords],  # Represent as just the points
            "distance_m": distance_m,
            "travel_time_s": travel_time_s,
        }
    

    def get_nearby_nodes(self, node, radius=50):
        """
        Get nearby nodes to the given node within a specified radius.
        :param node: The node ID to find nearby nodes for.
        :param radius: The search radius in meters.
        :return: List of nearby node IDs.
        """
        x, y = self.graph.nodes[node]["x"], self.graph.nodes[node]["y"]
        nearby_nodes = [
            n for n, attrs in self.graph.nodes(data=True)
            if self.straight_line_distance((y, x), (attrs["y"], attrs["x"])) <= radius
        ]
        return nearby_nodes

