# ============================================================
# COORDINATE / DISTANCE UTILITIES
# ============================================================
#
# This module handles:
#
# 1. Finding the nearest campus graph vertex.
# 2. Checking whether a location belongs to the self-routing
#    operating area.
# 3. Checking whether the kart has reached a destination.
#
# Coordinate formats supported by fnpp.to_tuple():
#
# {
#     "latitude": ...,
#     "longitude": ...
# }
#
# {
#     "lat": ...,
#     "lng": ...
# }
#
# {
#     "lats": ...,
#     "longs": ...
# }
#
# Pydantic/object:
#     coords.latitude
#     coords.longitude
# ============================================================


from ..navigation_tools.fnpp import (
    calculate_distance,
    to_tuple,
)

from ..self_navigation.polyline import (
    polypoints_db,
)


# ============================================================
# CONFIGURATION
# ============================================================

# Maximum distance from the campus reference point for
# enabling self/campus routing.
SELF_ROUTING_RADIUS = 1000.0  # metres


# Distance at which kart is considered to have reached
# marketplace/destination.
ARRIVAL_THRESHOLD = 7.0  # metres


# ============================================================
# INPUT NORMALIZATION
# ============================================================

def _normalize_coordinates(coords):
    """
    Convert supported coordinate formats into:

        {
            "lats": latitude,
            "longs": longitude
        }

    This is the format expected by older parts of the
    project, especially the campus graph utilities.
    """

    latitude, longitude = to_tuple(
        coords
    )

    return {
        "lats": latitude,
        "longs": longitude
    }


# ============================================================
# CLOSEST CAMPUS VERTEX
# ============================================================

def close_coords(current_coords):
    """
    Find the graph vertex geographically closest to the
    current coordinates.

    Parameters
    ----------
    current_coords:
        Kart/current GPS coordinates.

    Returns
    -------
    str or None:
        Name of the nearest graph vertex.

    Example:
        "A"

    None is returned if no valid graph vertex can be resolved.
    """

    # --------------------------------------------------------
    # Normalize current coordinates
    # --------------------------------------------------------

    try:

        current_point = to_tuple(
            current_coords
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    # --------------------------------------------------------
    # Search nearest vertex
    # --------------------------------------------------------

    closest_vertex = None
    shortest_distance = float("inf")

    for vertex, coordinates in (
        polypoints_db.items()
    ):

        try:

            vertex_point = (
                float(coordinates["lats"]),
                float(coordinates["longs"])
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            # Ignore malformed map data.
            continue

        distance = calculate_distance(
            current_point,
            vertex_point
        )

        if distance < shortest_distance:

            shortest_distance = distance
            closest_vertex = vertex

    return closest_vertex


# ============================================================
# CLOSEST VERTEX WITH DISTANCE
# ============================================================

def closest_vertex_info(current_coords):
    """
    Same nearest-vertex calculation as close_coords(), but
    also returns the actual distance.

    Useful for:
        - debugging
        - telemetry
        - map validation
        - future dashboard
    """

    try:

        current_point = to_tuple(
            current_coords
        )

    except (
        TypeError,
        ValueError
    ):

        return {
            "vertex": None,
            "distance_m": None
        }

    closest_vertex = None
    shortest_distance = float("inf")

    for vertex, coordinates in (
        polypoints_db.items()
    ):

        try:

            vertex_point = (
                float(coordinates["lats"]),
                float(coordinates["longs"])
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            continue

        distance = calculate_distance(
            current_point,
            vertex_point
        )

        if distance < shortest_distance:

            shortest_distance = distance
            closest_vertex = vertex

    if closest_vertex is None:

        return {
            "vertex": None,
            "distance_m": None
        }

    return {
        "vertex": closest_vertex,
        "distance_m": round(
            shortest_distance,
            2
        )
    }


# ============================================================
# SELF ROUTING AREA CHECK
# ============================================================

def check_self_dependence(
    kart_coords,
    marketplace_coords
):
    """
    Check whether the kart is close enough to the configured
    campus/self-routing area.

    Current project logic uses the marketplace as the second
    location reference.

    Returns:
        1 -> within self-routing radius
        0 -> outside self-routing radius
    """

    try:

        kart_point = to_tuple(
            kart_coords
        )

        marketplace_point = to_tuple(
            marketplace_coords
        )

    except (
        TypeError,
        ValueError
    ):

        return 0

    distance = calculate_distance(
        kart_point,
        marketplace_point
    )

    if distance <= SELF_ROUTING_RADIUS:
        return 1

    return 0


# ============================================================
# DIRECT DISTANCE CHECK
# ============================================================

def distance_between(
    point1,
    point2
):
    """
    Return geographic distance between two coordinate inputs
    in metres.
    This is a convenience wrapper around fnpp.calculate_distance().
    """
    try:
        p1 = to_tuple(
            point1
        )
        p2 = to_tuple(
            point2
        )
    except (
        TypeError,
        ValueError
    ):
        return float("inf")
    return calculate_distance(
        p1,
        p2
    )
# ============================================================
# DESTINATION ARRIVAL CHECK
# ============================================================
def very_close_coords(
    kart_coords,
    target_coords
):
    """
    Check whether the kart has reached a target location.
    Current threshold:
        <= 7 metres
    Returns:
        1 -> reached
        0 -> not reached
    """
    distance = distance_between(
        kart_coords,
        target_coords
    )
    if distance <= ARRIVAL_THRESHOLD:
        return 1
    return 0
# ============================================================
# ARRIVAL DISTANCE
# ============================================================
def arrival_distance(
    kart_coords,
    target_coords
):
    """
    Return current distance from kart to destination.
    Useful for:
        - dashboard
        - ETA systems
        - debugging
        - delivery tracking
    """
    distance = distance_between(
        kart_coords,
        target_coords
    )
    if distance == float("inf"):
        return None
    return round(
        distance,
        2
    )
# ============================================================
# EXPLICIT ARRIVAL CHECK
# ============================================================
def has_reached_destination(
    kart_coords,
    target_coords,
    threshold=ARRIVAL_THRESHOLD
):
    """
    Configurable destination arrival check.
    Returns:
        True / False
    """
    try:
        threshold = float(
            threshold
        )
    except (
        TypeError,
        ValueError
    ):
        threshold = ARRIVAL_THRESHOLD
    if threshold < 0:
        threshold = ARRIVAL_THRESHOLD
    distance = distance_between(
        kart_coords,
        target_coords
    )
    return distance <= threshold