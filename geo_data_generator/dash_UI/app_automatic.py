import random
from datetime import datetime
from dash import Dash, html, dcc, Input, Output, State, callback_context
import os
import sys
import dash_leaflet as dl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dash.exceptions import PreventUpdate
from models.person import Person
from common import (
    get_city_center,
    generate_map,
    add_waypoints_to_map,
    DEFAULT_CENTER_POINT,
    PERSON_TYPE_MAPPING,
    SPEED_RANGES,
)
from osm_integration import OSMManager

# Initialize the Dash app
app = Dash(__name__)
app.title = "Automatic Mode"

# Global variable for OSM manager
osm_manager = None

# App layout
app.layout = html.Div([
    html.H1("Automatic Mode - Interactive Map with Person Simulation"),

    dcc.Input(
        id="city-input",
        type="text",
        placeholder="Enter city name",
        style={"marginBottom": "10px"},
    ),
    html.Button("Set Center", id="set-center-btn", n_clicks=0),
    html.Div(id="city-output"),

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
    html.Button("Generate Trajectory", id="generate-btn", n_clicks=0),

    generate_map(DEFAULT_CENTER_POINT),  # Initial map

    html.Div(id="schedule-output", style={"marginTop": "10px"}),

    dcc.Input(
        id="time-input",
        type="text",
        placeholder="Enter time (HH:MM:SS)",
        style={"marginTop": "10px"}
    ),
    html.Button("Get Current Position", id="position-btn", n_clicks=0),
    html.Div(id="result-output"),
])


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

    lat, lon = get_city_center(city_name)
    osm_manager = OSMManager(center_point=(lat, lon), radius=10000)
    return f"Center point set to: ({lat}, {lon})", [lat, lon]


@app.callback(
    Output("person-store", "data"),
    Output("map", "children"),
    Output("schedule-output", "children"),
    Input("generate-btn", "n_clicks"),
    State("person-type-dropdown", "value"),
    State("map", "children"),
    prevent_initial_call=True,
)
def generate_person_and_trajectory(n_clicks, person_type, children):
    if not person_type or osm_manager is None:
        raise PreventUpdate

    # Get Person class and speed
    PersonClass = PERSON_TYPE_MAPPING.get(person_type)
    speed = random.uniform(*SPEED_RANGES[person_type])

    # Create a new Person instance
    person_instance = PersonClass(
        unique_id=1, person_type=person_type, speed=speed, osm_manager=osm_manager, mode="automatic"
    )

    # Serialize the person instance
    person_data = person_instance.to_dict()

    # Add waypoints and trajectories to the map
    map_components = add_waypoints_to_map(person_instance, osm_manager)

    # Generate readable schedule
    schedule_output = generate_schedule_output(person_instance)

    return person_data, children + map_components, schedule_output

def generate_schedule_output(person_instance):
    """
    Generate a detailed, human-readable schedule from the person's detailed schedule.
    :param person_instance: The Person instance containing the schedule.
    :return: A string representing the schedule.
    """
    if not person_instance.detail_schedule:
        return "No schedule available."

    schedule_lines = ["Detailed Schedule:"]
    for movement in person_instance.detail_schedule:
        schedule_lines.append(
            f"Departure: {movement['start_waypoint']} at {movement['start_time']} "
            f"→ Arrival: {movement['end_waypoint']} at {movement['arrival_time']} "
            f"(Distance: {movement['distance_m']:.2f} m, Travel Time: {movement['travel_time_s'] / 60:.2f} mins)"
        )

    return html.Div(
        [html.Div(line) for line in schedule_lines],
        style={"whiteSpace": "pre-line"}
    )

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
    if not time_str or not person_data:
        raise PreventUpdate

    try:
        current_time = datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        return children, "Invalid time format. Please use HH:MM:SS."

    # Deserialize the person instance and calculate the position
    person_instance = Person.from_dict(person_data, osm_manager)
    current_position, log = person_instance.get_position_at_time(current_time)

    # Highlight the route and position on the map
    current_route = [
        movement for movement in person_instance.detail_schedule
        if movement["start_time"] <= current_time.time() <= movement["arrival_time"]
    ]
    highlighted_route_coords = [
        (osm_manager.nodes.loc[node, "y"], osm_manager.nodes.loc[node, "x"])
        for node in current_route[0]["route_nodes"]
    ] if current_route else []

    # Create the highlighted route polyline
    highlighted_route = dl.Polyline(
        positions=highlighted_route_coords,
        color="red",  # Highlight the current route in red
        weight=5,
        opacity=0.8,
    )

    # Create a red marker for the current position
    current_position_marker = dl.Marker(
        position=current_position,
        children=dl.Tooltip(f"Current Position: {current_position}"),
        icon={
            "iconUrl": "https://maps.google.com/mapfiles/ms/icons/red-dot.png",  # Use a red icon URL
            "iconSize": [25, 41],  # Adjust the size of the icon
            "iconAnchor": [12, 41],  # Anchor the icon appropriately
        },
    )

    # current_position_marker = dl.DivMarker(
    #     position=current_position,
    #     iconOptions={
    #         "html": "<div style='background-color: red; width: 12px; height: 12px; border-radius: 50%;'></div>",
    #         "className": "custom-div-icon",
    #         "iconSize": [25, 25],
    #         "iconAnchor": [12, 12],
    #     },
    # )

    # Update map components
    updated_children = [child for child in children if not isinstance(child, dl.Polyline)] + [
        highlighted_route,
        current_position_marker,
    ]

    return updated_children, dcc.Markdown(log.replace("\n", "  \n"))


# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)