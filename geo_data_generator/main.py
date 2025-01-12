from osm_integration import OSMManager
from models.Adult import Adult
from datetime import datetime

def main():

    # Define the center point and radius for OSMManager
    center_point = (10.8231, 106.6297)  # Example: Ho Chi Minh City center
    radius = 10000  # 10 km radius

    # Initialize OSMManager
    osm_manager = OSMManager(center_point, radius, network_type="drive")

    # Create an adult person
    adult = Adult(unique_id=1, type="adult", speed=1.4, osm_manager=osm_manager)

    # Print the assigned waypoints
    print("\n--- Assigned Waypoints ---")
    for waypoint, coords in adult.waypoints.items():
        if coords:
            print(f"{waypoint.capitalize()}: {coords}")

    # Print the schedule
    print("\n--- Schedule ---")
    for movement in adult.schedule:
        print(f"{movement['start_waypoint']} → {movement['end_waypoint']} at {movement['start_time']}")

    # Print the detailed schedule with trajectories
    print("\n--- Detailed Schedule ---")
    for movement in adult.detail_schedule:
        print(f"{movement['start_waypoint']} → {movement['end_waypoint']}")
        print(f"  Start Time: {movement['start_time']}")
        print(f"  Arrival Time: {movement['arrival_time']}")
        print(f"  Distance: {movement['distance_m']} meters")
        print(f"  Travel Time: {movement['travel_time_s']} seconds")
        print(f"  Route Nodes: {movement['route_nodes']}")

    # Simulate position at a specific time
    current_time = datetime.now().replace(hour=7, minute=30)  # Example time
    position = adult.get_position_at_time(current_time)

    print("\n--- Simulated Position ---")
    print(f"Time: {current_time}")
    print(f"Position (latitude, longitude): {position}")


if __name__ == "__main__":
    main()