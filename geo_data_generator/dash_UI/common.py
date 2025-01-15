import os
import sys
from geopy.geocoders import Nominatim
import dash_leaflet as dl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Assume OSMManager, Person, Adult, Child, Older are available in the same directory
from models.person import Person
from models.adult import Adult
from models.child import Child
from models.older import Older

# Default center point
DEFAULT_CENTER_POINT = (10.8231, 106.6297)  # Ho Chi Minh City

# Mapping from person type to class
PERSON_TYPE_MAPPING = {
    "adult": Adult,
    "child": Child,
    "older": Older,
}

# Speed ranges
SPEED_RANGES = {
    "child": (0.8, 1.4),  # Walking speed: ~3-5 km/h
    "adult": (8.3, 11.1),  # Car speed: ~30-40 km/h
    "older": (0.8, 1.4),  # Walking speed: ~3-5 km/h
}


def get_city_center(city_name):
    """
    Fetch the center point of the city using geocoding.
    :param city_name: Name of the city.
    :return: Tuple (latitude, longitude) representing the city center.
    """
    try:
        geolocator = Nominatim(user_agent="geo_data_generator")
        location = geolocator.geocode(city_name)
        if location:
            print(f"Center point of {city_name}: ({location.latitude}, {location.longitude})")
            return location.latitude, location.longitude
        else:
            raise ValueError(f"City '{city_name}' not found.")
    except Exception as e:
        print(f"Error fetching center point for city '{city_name}': {e}")
        return DEFAULT_CENTER_POINT  # Default fallback


def generate_map(center_point):
    """
    Generate a Dash Leaflet map component.
    :param center_point: Tuple (latitude, longitude).
    :return: Dash Leaflet map component.
    """
    return dl.Map(
        id="map",
        center=center_point,
        zoom=13,
        children=[
            dl.TileLayer(),  # Base layer
            dl.FullScreenControl(),
            dl.GestureHandling()
        ],
        
        style={"height": "80vh", "width": "100%"},
    )


def add_waypoints_to_map(person_instance, osm_manager):
    """
    Add waypoints and trajectories to the map for the given person instance.
    :param person_instance: Instance of a Person subclass.
    :param osm_manager: Instance of OSMManager.
    :return: List of map components (polylines and markers).
    """
    polylines = []
    for movement in person_instance.detail_schedule:
        route_coords = [
            (osm_manager.nodes.loc[node, "y"], osm_manager.nodes.loc[node, "x"])
            for node in movement["route_nodes"]
        ]
        polylines.append(
            dl.Polyline(
                positions=route_coords,
                color="blue",
                weight=3,
                opacity=0.8,
            )
        )

    markers = [
        dl.Marker(position=coords, children=dl.Tooltip(waypoint.capitalize()))
        for waypoint, coords in person_instance.waypoints.items() if coords
    ]

    return polylines + markers