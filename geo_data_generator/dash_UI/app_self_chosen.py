import sys
import os
from datetime import time, datetime
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dash
from dash import html, dcc, Input, Output, State
import dash_leaflet as dl
from dash.exceptions import PreventUpdate
from common import (
    get_city_center,
    add_waypoints_to_map,
    DEFAULT_CENTER_POINT,
    PERSON_TYPE_MAPPING,
    SPEED_RANGES,
)
from models.person import Person
from osm_integration import OSMManager

# Initialize app
app = dash.Dash(__name__)
app.title = "Self-Chosen Mode with EditControl"

# Initialize global variables
osm_manager = None

# App layout
app.layout = html.Div([
    html.H1("Self-Chosen Mode"),
    dcc.Input(id="city-input", type="text", placeholder="Enter city name", style={"margin-bottom": "10px"}),
    html.Button("Set Center", id="set-center-btn", n_clicks=0),
    html.Div(id="city-output"),

    # Map with EditControl
    dl.Map(
        id="map",
        center=DEFAULT_CENTER_POINT,
        zoom=13,
        children=[
            dl.TileLayer(),  # Base layer
            dl.FullScreenControl(),
            dl.FeatureGroup([
                dl.EditControl(
                    id="edit-control",
                    position="topleft",
                    draw={
                        "marker": True,
                        "polygon": False,
                        "polyline": False,
                        "rectangle": False,
                        "circle": False,
                        "circlemarker": False,
                    },
                ),
            ]),
        ],
        style={"height": "70vh", "width": "100%"},
    ),

    html.Div([
        html.Button("Choose a waypoint", id="toggle-btn", n_clicks=0),
    ], style={"margin-top": "20px"}),

    html.Div(id="waypoints-list", style={"margin-top": "20px"}),

    html.H3("Rename Waypoints"),
    dcc.Dropdown(id="waypoint-dropdown", placeholder="Select a waypoint to rename", style={"font-family": "Arial", "width":"50%", "font-size": "14px", "margin": " 5px 5px 10px 5px"}),
    dcc.Input(id="new-waypoint-name", type="text", placeholder="Enter new waypoint name"),
    html.Button("Rename Waypoint", id="rename-btn", n_clicks=0),
    html.Div(id="rename-status", style={"margin-top": "10px", "color": "blue"}),

    # Store for waypoints
    dcc.Store(id="waypoints-store"),

    html.H3("Create Schedule"),
    html.Div([
        dcc.Dropdown(id="start-waypoint", placeholder="Select start waypoint", style={"font-family": "Arial", "width":"50%", "font-size": "14px", "margin": " 5px 5px 10px 5px"}),
        dcc.Dropdown(id="end-waypoint", placeholder="Select end waypoint", style={"font-family": "Arial", "width":"50%", "font-size": "14px", "margin": " 5px 5px 10px 5px"}),
        dcc.Input(id="start-time", type="text", placeholder="Start time (HH:MM)"),
        html.Button("Add to Schedule", id="add-schedule-btn", n_clicks=0),
        html.Div(id="schedule-status", style={"margin-top": "10px", "color": "green"}),
    ], style={"margin-top": "20px"}),

    html.H3("Current Schedule"),
    html.Div(id="schedule-list", style={"margin-top": "20px"}),

    # Store for schedule
    dcc.Store(id="schedule-store"),

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

    dcc.Input(
        id="time-input",
        type="text",
        placeholder="Enter time (HH:MM:SS)",
        style={"marginTop": "10px"}
    ),
    html.Button("Get Current Position", id="position-btn", n_clicks=0),
    html.Div(id="result-output"),
])

# Callbacks
@app.callback(
    Output("edit-control", "drawToolbar"),
    Input("toggle-btn", "n_clicks"),
    prevent_initial_call=True,
)
def choose_waypoint(n_clicks):
    """
    Activate marker placement mode.
    """
    return {"mode": "marker", "n_clicks": n_clicks} # For edit-control.drawToolbar

@app.callback(
    Output("city-output", "children"),
    Output("map", "center"),
    Input("set-center-btn", "n_clicks"),
    State("city-input", "value"),
    prevent_initial_call=True,
)
def update_center_by_city(n_clicks, city_name):
    """
    Update the map center to the selected city.
    """
    global osm_manager
    if not city_name:
        raise PreventUpdate
    lat, lon = get_city_center(city_name)
    osm_manager = OSMManager(center_point=(lat, lon), radius=10000)
    return f"City center set to: {city_name} ({lat}, {lon})", [lat, lon]

@app.callback(
    Output("waypoints-store", "data"),
    Output("waypoints-list", "children"),
    Output("waypoint-dropdown", "options"),
    Output("start-waypoint", "options"),
    Output("end-waypoint", "options"),
    Input("edit-control", "geojson"),
    prevent_initial_call=True,
)
def save_waypoints(geojson_data):
    """Save the waypoints selected using the EditControl into a dictionary."""
    waypoints = {}
    features = geojson_data.get("features", [])
    for feature in features:
        if feature["geometry"]["type"] == "Point":
            coords = feature["geometry"]["coordinates"]
            waypoint_name = f"Waypoint {len(waypoints) + 1}"
            waypoints[waypoint_name] = (coords[1], coords[0])  # GeoJSON uses [lng, lat]

    # Generate waypoint list UI and dropdown options
    waypoint_list_ui = [html.Div(f"{name}: {coord}") for name, coord in waypoints.items()]
    dropdown_options = [{"label": name, "value": name} for name in waypoints.keys()]
    return waypoints, waypoint_list_ui, dropdown_options, dropdown_options, dropdown_options

@app.callback(
    Output("waypoints-store", "data", allow_duplicate=True),
    Output("waypoints-list", "children",allow_duplicate=True),
    Output("rename-status", "children"),
    Output("waypoint-dropdown", "options", allow_duplicate=True),
    Output("start-waypoint", "options", allow_duplicate=True),
    Output("end-waypoint", "options", allow_duplicate=True),
    Input("rename-btn", "n_clicks"),
    State("waypoint-dropdown", "value"),
    State("new-waypoint-name", "value"),
    State("waypoints-store", "data"),
    prevent_initial_call=True,
)
def rename_waypoint(n_clicks, selected_waypoint, new_name, waypoints):
    """Rename a selected waypoint."""
    if not selected_waypoint or not new_name:
        raise PreventUpdate

    waypoints = waypoints or {}
    if selected_waypoint not in waypoints:
        return waypoints, dash.no_update, f"Waypoint '{selected_waypoint}' not found."

    # Rename the waypoint
    coords = waypoints.pop(selected_waypoint)
    waypoints[new_name] = coords
    dropdown_options = [{"label": name, "value": name} for name in waypoints.keys()]
    waypoint_list_ui = [html.Div(f"{name}: {coord}") for name, coord in waypoints.items()]
    return waypoints, waypoint_list_ui, f"Renamed {selected_waypoint} to {new_name}.", dropdown_options, dropdown_options, dropdown_options

@app.callback(
    Output("schedule-store", "data"),
    Output("schedule-list", "children"),
    Output("schedule-status", "children"),
    Input("add-schedule-btn", "n_clicks"),
    State("start-waypoint", "value"),
    State("end-waypoint", "value"),
    State("start-time", "value"),
    State("schedule-store", "data"),
    prevent_initial_call=True,
)
def add_schedule(n_clicks, start_waypoint, end_waypoint, start_time, schedule):
    """Add an entry to the schedule."""
    if not start_waypoint or not end_waypoint or not start_time:
        return schedule, dash.no_update, "Please fill all fields to add a schedule."
    if start_waypoint == end_waypoint:
        return schedule, dash.no_update, "Start and end waypoints must be different."

    try:
        hours, minutes = map(int, start_time.split(":"))
        start_time_obj = time(hours, minutes)
    except ValueError:
        return schedule, dash.no_update, "Invalid time format. Use HH:MM."

    schedule = schedule or []
    schedule.append({
        "start_time": start_time_obj,
        "start_waypoint": start_waypoint,
        "end_waypoint": end_waypoint,
    })

    schedule_list_ui = [
        html.Div(f"{entry['start_time']} - {entry['start_waypoint']} → {entry['end_waypoint']}")
        for entry in schedule
    ]
    return schedule, schedule_list_ui, "Schedule entry added."


@app.callback(
    Output("person-store", "data"),
    Output("map", "children"),
    Output("schedule-list", "children", allow_duplicate=True),
    Input("generate-btn", "n_clicks"),
    State("person-type-dropdown", "value"),
    State("map", "children"),
    State("schedule-store", "data"),
    State("waypoints-store", "data"),
    prevent_initial_call=True,
)
def generate_person_and_trajectory(n_clicks, person_type, children, schedule, waypoints):
    if not person_type or osm_manager is None:
        raise PreventUpdate

    # Get Person class and speed
    speed = random.uniform(*SPEED_RANGES[person_type])

    # Create a new Person instance
    person_instance = Person(
        unique_id=1, person_type=person_type, speed=speed, osm_manager=osm_manager,predefined_waypoints=waypoints, schedule=schedule, detail_schedule=[], mode="self_chosen", 
    )

    # Serialize the person instance
    person_data = person_instance.to_dict()

    # Add waypoints and trajectories to the map
    map_components = add_waypoints_to_map(person_instance, osm_manager)

    # Generate readable schedule
    schedule_output = generate_schedule_output(person_instance)

    updated_children = [child for child in children if not isinstance(child, dl.Polyline)]
    return person_data, updated_children + map_components, schedule_output

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

if __name__ == "__main__":
    app.run_server(debug=True)