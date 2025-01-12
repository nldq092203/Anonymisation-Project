# Geo Data Generator

Geo Data Generator is a Python-based project that simulates human activity and movement within a specified geographic area. It uses OpenStreetMap (OSM) data to create realistic schedules, trajectories, and positions for different types of people (e.g., children, adults, and older individuals) and records their activities over a defined survey period.

## Features

- **Dynamic Geocoding**: Automatically determine the center point of a city using its name.
- **OSM Integration**: Load road networks and features (e.g., schools, parks, markets) from OpenStreetMap.
- **Person Simulation**: Simulate different types of people with realistic movement patterns:
    - Children: Travel to school, parks, etc., usually by bus.
    - Adults: Commute to workplaces, gyms, markets, usually by car.
    - Older individuals: Walk to healthcare centers, parks, etc.
- **Trajectory Calculation**: Calculate the shortest path and travel time between waypoints using network graphs.
- **Activity Simulation**: Generate realistic daily activity data for a survey period, including timestamps and positions.
- **Data Export**: Save simulated data to CSV for further analysis.
- **Folium Map Visualization**: Visualize trajectories and activity data on an interactive map.

## Person Class Schema

![Person Schema](geo_data_generator/images/models_Person_schema.png)

## System Overview

![System Overview](geo_data_generator/images/overview.png)

## Example Map Visualization

Below is an example of a map visualization showing the trajectory, waypoints and the current positon of a simulated person in Paris:
- **Red Line**: Represents the trajectory (shortest path) the simulated person follows.
- **Blue Markers**: Indicate predefined waypoints, such as home, workplace, or park.
- **Green Marker**: Shows the current position of the person at a specific timestamp during the simulation.

![Map Visualization](geo_data_generator/images/track_trace.png)