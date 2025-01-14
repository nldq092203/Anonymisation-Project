import sys
import os
import random

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dash
from dash import html, dcc, Input, Output, State
import dash_leaflet as dl
from dash.exceptions import PreventUpdate
from datetime import datetime
from geopy.geocoders import Nominatim

# Assume Person and OSMManager classes are available in the same directory
from models.person import Person
from models.adult import Adult
from models.child import Child
from models.older import Older
from osm_integration import OSMManager

# Create the Dash app
app = dash.Dash(__name__)

# Initialize global variables
osm_manager = None
center_point = (10.8231, 106.6297)  # Default center point (e.g., Ho Chi Minh City)

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
        return center_point  # Default fallback

# App layout
app.layout = html.Div([
    html.H1("Interactive Map with Person Simulation"),
    
    dcc.Input(
        id="city-input",
        type="text",
        placeholder="Enter city name",
        style={"margin-bottom": "10px"},
    ),
    html.Button("Set Center", id="set-center-btn", n_clicks=0),
    html.Div(id="city-output"),
    
    dcc.Dropdown(
        id="mode-dropdown",
        options=[
            {"label": "Automatic", "value": "automatic"},
            {"label": "Self-chosen", "value": "self_chosen"},
        ],
        placeholder="Select Mode",
        style={"font-family": "Arial", "width":"50%", "font-size": "14px", "margin": " 5px 5px 10px 5px"},
    ),
    
    dcc.Dropdown(
        id="person-type-dropdown",
        options=[
            {"label": "Adult", "value": "adult"},
            {"label": "Older", "value": "older"},
            {"label": "Child", "value": "child"},
        ],
        placeholder="Select Person Type",
        style={"font-family": "Arial", "width":"50%", "font-size": "14px", "margin": " 5px 5px 10px 5px"},
    ),
    dcc.Store(id="person-store"),  # Store for person instance
    html.Button("Generate Person and Trajectory", id="generate-btn", n_clicks=0),    
    dl.Map(
        id="map",
        center=center_point,
        zoom=13,
        children=[
            dl.TileLayer(),  # Base layer
        ],
        style={"height": "80vh", "width": "100%"},
    ),
    
    html.Div(id="schedule-output", style={"margin-top": "10px"}),

    dcc.Input(
        id="time-input",
        type="text",
        placeholder="Enter time (HH:MM:SS)",
        style={"margin-top": "10px"}
    ),
    html.Button("Get Current Position", id="position-btn", n_clicks=0),
    html.Div(id="result-output"),
])

# Mapping from person type to the corresponding class
PERSON_TYPE_MAPPING = {
    "adult": Adult,
    "child": Child,
    "older": Older,
}

# Speed ranges for different person types
SPEED_RANGES = {
    "child": (0.8, 1.4),  # Walking speed: ~3-5 km/h
    "adult": (8.3, 11.1),  # Car speed: ~30-40 km/h
    "older": (0.8, 1.4),  # Walking speed: ~3-5 km/h
}

@app.callback(
    Output("city-output", "children"),
    Output("map", "center"),
    Input("set-center-btn", "n_clicks"),
    State("city-input", "value"),
)
def update_center_by_city(n_clicks, city_name):
    global osm_manager
    if n_clicks == 0 or not city_name:
        raise PreventUpdate

    # Get the city center using geocoding
    lat, lon = get_city_center(city_name)
    osm_manager = OSMManager(center_point=(lat, lon), radius=10000)
    return f"Center point set to: ({lat}, {lon})", [lat, lon]

@app.callback(
    Output("person-store", "data"),
    Output("map", "children", allow_duplicate=True),
    Output("schedule-output", "children"),
    Input("generate-btn", "n_clicks"),
    State("mode-dropdown", "value"),
    State("person-type-dropdown", "value"),
    State("map", "children"),
    prevent_initial_call=True
)
def generate_person_and_trajectory(n_clicks, mode, person_type, children):
    if n_clicks == 0 or not mode or not person_type or osm_manager is None:
        raise PreventUpdate

    # Get the Person class and speed
    PersonClass = PERSON_TYPE_MAPPING.get(person_type)
    if not PersonClass:
        return children, "Invalid person type selected.", ""

    speed = random.uniform(*SPEED_RANGES[person_type])

    # Create a new Person instance
    person_instance = PersonClass(
        unique_id=1, person_type=person_type, speed=speed, osm_manager=osm_manager, mode=mode
    )

    # Serialize the person instance to a dictionary for storage
    person_data = person_instance.to_dict()

    # Generate waypoints and trajectory
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

    # Add markers for waypoints
    markers = [
        dl.Marker(position=coords, children=dl.Tooltip(waypoint.capitalize()))
        for waypoint, coords in person_instance.waypoints.items() if coords
    ]

    # Prepare schedule output
    schedule = "\n".join(
        f"{movement['start_time']} - {movement['end_waypoint']}"
        for movement in person_instance.detail_schedule
    )

    return person_data, [dl.TileLayer()] + polylines + markers, f"Schedule:\n{schedule}"

@app.callback(
    Output("map", "children", allow_duplicate=True),
    Output("result-output", "children"),
    Input("position-btn", "n_clicks"),
    State("time-input", "value"),
    State("person-store", "data"),
    State("map", "children"),
    prevent_initial_call=True,
)
def get_current_position(n_clicks, time_str, person_data, children):
    if n_clicks == 0 or not time_str or not person_data:
        raise PreventUpdate

    # Parse the time
    try:
        current_time = datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        return children, "Invalid time format. Please use HH:MM:SS."

    # Deserialize the person instance
    person_instance = Person.from_dict(person_data, osm_manager)

    # Get current position
    current_position, log = person_instance.get_position_at_time(current_time)
    print(f"Calculated current position: {current_position}")

    if current_position is None:
        return children, "Could not determine the current position."

    # Find the current route based on the time
    current_route = None
    for movement in person_instance.detail_schedule:
        if movement["start_time"] <= current_time.time() <= movement["arrival_time"]:
            current_route = movement
            break

    if not current_route:
        return children, "No active route at the given time."

    # Highlight the current route
    highlighted_route_coords = [
        (osm_manager.nodes.loc[node, "y"], osm_manager.nodes.loc[node, "x"])
        for node in current_route["route_nodes"]
    ]
    highlighted_route = dl.Polyline(
        positions=highlighted_route_coords,
        color="red",  # Highlight the current route in red
        weight=5,
        opacity=0.8,
    )

    # Add marker for the current position
    current_position_marker = dl.Marker(
        position=[current_position[0], current_position[1]],
        children=dl.Tooltip(f"Current Position: {current_position}"),
        icon={
            "iconUrl": "https://maps.google.com/mapfiles/ms/icons/red-dot.png",  # Red marker icon URL
            "iconSize": [25, 41],
            "iconAnchor": [12, 41],
        },
    )

    # Replace the highlighted route in the map children
    updated_children = [child for child in children if not isinstance(child, dl.Polyline)]
    updated_children += [highlighted_route, current_position_marker]

    return updated_children, dcc.Markdown(log.replace("\n", "  \n"))

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)