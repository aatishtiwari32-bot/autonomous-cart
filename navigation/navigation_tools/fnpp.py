import math


# ============================================================
# CONFIGURATION
# ============================================================

EARTH_RADIUS_METERS = 6371000.0

# A waypoint is considered reached when the kart comes
# within this distance of it.
WAYPOINT_REACHED_RADIUS = 10.0  # meters

# Number of points to look ahead for smoother steering.
# Example:
# current_index = 5
# lookahead = 2
# target_index = 7
WAYPOINT_LOOKAHEAD = 2


# ============================================================
# DISTANCE
# ============================================================

def calculate_distance(point1, point2):
    """
    Calculate great-circle distance between two GPS points.

    Input:
        point1 = (latitude, longitude)
        point2 = (latitude, longitude)

    Returns:
        Distance in meters as float.
    """

    if point1 is None or point2 is None:
        return float("inf")

    lat1, lon1 = point1
    lat2, lon2 = point2

    # Convert degrees to radians
    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))

    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    # Difference in radians
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Haversine formula
    a = (
        math.sin(delta_lat / 2.0) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2.0) ** 2
    )

    # Protect against tiny floating-point errors
    a = max(0.0, min(1.0, a))

    c = 2.0 * math.atan2(
        math.sqrt(a),
        math.sqrt(1.0 - a)
    )

    return EARTH_RADIUS_METERS * c


# ============================================================
# COORDINATE NORMALIZATION
# ============================================================

def to_tuple(coords):
    """
    Convert different coordinate formats into:

        (latitude, longitude)

    Supported formats:

    1. Tuple:
        (24.4355, 77.1622)

    2. List:
        [24.4355, 77.1622]

    3. Dictionary:
        {
            "latitude": 24.4355,
            "longitude": 77.1622
        }

    4. Dictionary:
        {
            "lat": 24.4355,
            "lng": 77.1622
        }

    5. Dictionary used by your campus graph:
        {
            "lats": 24.4355,
            "longs": 77.1622
        }

    6. Pydantic model:
        coords.latitude
        coords.longitude

    Returns:
        (latitude, longitude)

    Raises:
        ValueError if the coordinate format is invalid.
    """

    if coords is None:
        raise ValueError("Coordinates cannot be None")

    # --------------------------------------------------------
    # Tuple / List
    # --------------------------------------------------------

    if isinstance(coords, (tuple, list)):

        if len(coords) < 2:
            raise ValueError(
                "Coordinate sequence must contain latitude and longitude"
            )

        latitude = float(coords[0])
        longitude = float(coords[1])

        return latitude, longitude

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(coords, dict):

        # Standard API format
        if (
            "latitude" in coords
            and "longitude" in coords
        ):
            return (
                float(coords["latitude"]),
                float(coords["longitude"])
            )

        # Short format
        if (
            "lat" in coords
            and "lng" in coords
        ):
            return (
                float(coords["lat"]),
                float(coords["lng"])
            )

        # Your internal map format
        if (
            "lats" in coords
            and "longs" in coords
        ):
            return (
                float(coords["lats"]),
                float(coords["longs"])
            )

        raise ValueError(
            "Dictionary must contain either "
            "(latitude, longitude), "
            "(lat, lng), or "
            "(lats, longs)"
        )

    # --------------------------------------------------------
    # Pydantic / object with latitude and longitude
    # --------------------------------------------------------

    if hasattr(coords, "latitude") and hasattr(coords, "longitude"):

        return (
            float(coords.latitude),
            float(coords.longitude)
        )

    # --------------------------------------------------------
    # Unsupported type
    # --------------------------------------------------------

    raise ValueError(
        f"Unsupported coordinate type: {type(coords).__name__}"
    )


# ============================================================
# LEGACY CLOSEST POINT FUNCTION
# ============================================================

def polypoint(current_coords, points):
    """
    Find the geographically closest point from a list of route points.

    This function is retained for backward compatibility with
    older parts of the project.

    NOTE:
    For actual navigation, use get_next_waypoint().
    """

    if not points:
        return None

    current = to_tuple(current_coords)

    closest_point = None
    shortest_distance = float("inf")

    for point in points:

        try:
            route_point = to_tuple(point)
        except ValueError:
            # Ignore malformed route point
            continue

        distance = calculate_distance(
            current,
            route_point
        )

        if distance < shortest_distance:

            shortest_distance = distance
            closest_point = point

    return closest_point


# ============================================================
# PROGRESSIVE WAYPOINT TRACKER
# ============================================================

def get_next_waypoint(
    current_coords,
    points,
    current_index
):
    """
    Progressively track the kart through a route.

    Unlike polypoint(), this function does NOT keep searching
    the entire route for the nearest point.

    It remembers the current waypoint index and only moves
    forward through the route.

    Parameters
    ----------
    current_coords:
        Current kart GPS coordinates.

    points:
        Complete route waypoint list.

    current_index:
        Index of the waypoint currently being tracked.

    Returns
    -------
    tuple:
        (
            target_waypoint,
            updated_waypoint_index
        )

    target_waypoint:
        (latitude, longitude), or None when route is complete.

    updated_waypoint_index:
        New progress index.
    """

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if not points:
        return None, current_index

    try:
        current_index = int(current_index)
    except (TypeError, ValueError):
        current_index = 0

    # Never allow negative indexes
    current_index = max(0, current_index)

    # If already beyond route
    if current_index >= len(points):
        return None, current_index

    current = to_tuple(current_coords)

    # --------------------------------------------------------
    # STEP 1:
    # Advance through already-reached waypoints
    # --------------------------------------------------------
    while current_index < len(points):
        waypoint = to_tuple(points[current_index])
        distance = calculate_distance(
            current,
            waypoint
        )
        if distance <= WAYPOINT_REACHED_RADIUS:
            current_index += 1
        else:
            break
    # --------------------------------------------------------
    # STEP 2:
    # Entire route completed
    # --------------------------------------------------------
    if current_index >= len(points):
        return None, current_index
    # --------------------------------------------------------
    # STEP 3:
    # Look ahead
    # --------------------------------------------------------
    target_index = min(
        current_index + WAYPOINT_LOOKAHEAD,
        len(points) - 1
    )
    target_waypoint = to_tuple(
        points[target_index]
    )
    return target_waypoint, current_index
# ============================================================
# OPTIONAL WAYPOINT DISTANCE HELPER
# ============================================================
def distance_to_waypoint(
    current_coords,
    waypoint
):
    """
    Return distance from current kart position to a waypoint.
    Useful for debugging, telemetry, and future dashboard use.
    """
    current = to_tuple(current_coords)
    target = to_tuple(waypoint)
    return calculate_distance(
        current,
        target
    )
# ============================================================
# ROUTE COMPLETION HELPER
# ============================================================
def is_route_complete(
    current_coords,
    points,
    current_index
):
    """
    Check whether the kart has completed the route.
    Returns:
        True / False
    """
    if not points:
        return True
    try:
        current_index = int(current_index)
    except (TypeError, ValueError):
        return False
    # Already beyond final waypoint
    if current_index >= len(points):
        return True
    current = to_tuple(current_coords)
    final_point = to_tuple(
        points[-1]
    )
    distance = calculate_distance(
        current,
        final_point
    )
    return distance <= WAYPOINT_REACHED_RADIUS