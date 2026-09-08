import math
ARRIVAL_THRESHOLD = 10.0   # metres
from distance import calculate_distance
from polyline import polypoints_db
def close_coords(current_coords):
    current_point = (
        current_coords["lats"],
        current_coords["longs"]
    )
    closest_vertex = None
    shortest_distance = float("inf")
    for vertex, coordinates in polypoints_db.items():
        vertex_point = (
            coordinates["lats"],
            coordinates["longs"]
        )
        distance = calculate_distance(
            current_point,
            vertex_point
        )
        if distance < shortest_distance:
            shortest_distance = distance
            closest_vertex = vertex
    return closest_vertex

def check_self_dependence(kart_coords, marketplace_coords):
    dependence_THRESHOLD = 1000.0 #metres
    # Kart coordinates
    lat1 = kart_coords["lats"]
    lon1 = kart_coords["longs"]
    # Marketplace coordinates
    lat2 = marketplace_coords["lats"]
    lon2 = marketplace_coords["longs"]
    # Degrees -> radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    # Differences
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )
    EARTH_RADIUS = 6371000  # metres
    distance = EARTH_RADIUS * c
    if distance <= dependence_THRESHOLD:
        return 1
    return 0