import osmnx as ox
import folium
from shapely.geometry import LineString
from folium.plugins import MarkerCluster

center_point = (40.7128, -74.0060)
graph = ox.graph_from_point(center_point, dist=2000, network_type="drive")
nodes, edges = ox.graph_to_gdfs(graph)

# Create map Folium
center = [nodes['y'].mean(), nodes['x'].mean()]
m = folium.Map(location=center, zoom_start=12)

for _, row in edges.iterrows():
    line = row['geometry'].simplify(0.001)  
    folium.PolyLine(
        locations=[(coord[1], coord[0]) for coord in line.coords],
        color="blue",
        weight=2,
        opacity=0.8
    ).add_to(m)

# Cluster maker
marker_cluster = MarkerCluster().add_to(m)
for _, row in nodes.sample(frac=0.1).iterrows():  # Get 10% nodes
    folium.Marker(
        location=[row['y'], row['x']],
        popup=f"Node {row.name}"
    ).add_to(marker_cluster)

# Save map
m.save("optimized_map.html")
print("Map saved as optimized_map.html")