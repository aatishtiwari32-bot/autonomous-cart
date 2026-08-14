import math
def calculate_distance(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
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
    EARTH_RADIUS = 6371000
    return EARTH_RADIUS * c


def polypoint(current_coords, points):
    if not points:
        return None
    current = (
        current_coords.latitude,
        current_coords.longitude
    )
    closest_point = None
    shortest_distance = float("inf")
    for point in points:
        route_point = (
            point["latitude"],
            point["longitude"]
        )
        distance = calculate_distance(
            current,
            route_point
        )
        if distance < shortest_distance:
            shortest_distance = distance
            closest_point = point
    return closest_point