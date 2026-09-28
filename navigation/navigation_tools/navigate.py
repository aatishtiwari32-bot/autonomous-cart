import math

from .fnpp import (
    get_next_waypoint,
    to_tuple,
    calculate_distance
)


# ============================================================
# NAVIGATION CONFIGURATION
# ============================================================

# Maximum heading error for moving straight.
FORWARD_ANGLE_THRESHOLD = 10.0

# Heading error range for slight steering.
SLIGHT_TURN_THRESHOLD = 30.0


# ============================================================
# BEARING CALCULATION
# ============================================================

def calculate_bearing(point1, point2):
    """
    Calculate the initial geographic bearing from point1 to point2.

    Bearing convention:
        0°   -> North
        90°  -> East
        180° -> South
        270° -> West

    Parameters
    ----------
    point1:
        Current coordinate.

    point2:
        Target coordinate.

    Returns
    -------
    float:
        Bearing in degrees [0, 360).
    """

    lat1, lon1 = to_tuple(point1)
    lat2, lon2 = to_tuple(point2)

    # Convert latitude to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    # Longitude difference in radians
    delta_lon = math.radians(lon2 - lon1)

    # Geographic bearing formula
    y = (
        math.sin(delta_lon)
        * math.cos(lat2_rad)
    )

    x = (
        math.cos(lat1_rad)
        * math.sin(lat2_rad)
        -
        math.sin(lat1_rad)
        * math.cos(lat2_rad)
        * math.cos(delta_lon)
    )

    bearing = math.atan2(y, x)

    # Radians -> degrees
    bearing = math.degrees(bearing)

    # Normalize to 0-360
    bearing = (bearing + 360.0) % 360.0

    return bearing


# ============================================================
# ANGLE DIFFERENCE
# ============================================================

def angle_difference(desired_bearing, current_bearing):
    """
    Calculate the shortest signed angular difference.

    Result range:
        -180° to +180°

    Positive:
        Target is to the RIGHT.

    Negative:
        Target is to the LEFT.
    """

    difference = (
        desired_bearing
        - current_bearing
    )

    difference = (
        difference + 180.0
    ) % 360.0 - 180.0

    return difference


# ============================================================
# HEADING NORMALIZATION
# ============================================================

def normalize_heading(heading):
    """
    Normalize a heading to the range [0, 360).
    """

    try:
        heading = float(heading)
    except (TypeError, ValueError):
        raise ValueError(
            "Heading must be a numeric value"
        )

    return heading % 360.0


# ============================================================
# COMMAND GENERATION
# ============================================================

def generate_command(angle_error):
    """
    Convert heading error into a movement command.

    Command logic:

        |error| <= 10°
            -> F

        +10° to +30°
            -> SR

        -10° to -30°
            -> SL

        > +30°
            -> R

        < -30°
            -> L
    """

    if abs(angle_error) <= FORWARD_ANGLE_THRESHOLD:
        return "F"

    elif (
        FORWARD_ANGLE_THRESHOLD
        < angle_error
        <= SLIGHT_TURN_THRESHOLD
    ):
        return "SR"

    elif (
        -SLIGHT_TURN_THRESHOLD
        <= angle_error
        < -FORWARD_ANGLE_THRESHOLD
    ):
        return "SL"

    elif angle_error > SLIGHT_TURN_THRESHOLD:
        return "R"

    else:
        return "L"


# ============================================================
# MAIN NAVIGATION FUNCTION
# ============================================================

def navigate(
    heading,
    current_coords,
    points,
    waypoint_index=0
):
    """
    Navigate the cart through a complete GPS waypoint route.

    Parameters
    ----------
    heading:
        Current kart heading from IMU/compass in degrees.

    current_coords:
        Current kart GPS coordinates.

    points:
        Complete list of route waypoints.

    waypoint_index:
        Current progress index in the route.

    Returns
    -------
    dict:

        Normal case:
        {
            "command": "F",
            "waypoint_index": 3,
            "route_complete": False,
            "target_waypoint": (...),
            "distance_to_target": 18.4,
            "desired_bearing": 92.6,
            "angle_error": -4.2
        }

        Route complete:
        {
            "command": "STOP",
            "waypoint_index": ...,
            "route_complete": True,
            ...
        }

        Empty route:
        {
            "command": "STOP",
            "waypoint_index": ...,
            "route_complete": True,
            ...
        }
    """

    # --------------------------------------------------------
    # Validate route
    # --------------------------------------------------------

    if not points:
        return {
            "command": "STOP",
            "waypoint_index": waypoint_index,
            "route_complete": True,
            "target_waypoint": None,
            "distance_to_target": 0.0,
            "desired_bearing": None,
            "angle_error": None
        }

    # --------------------------------------------------------
    # Normalize waypoint index
    # --------------------------------------------------------

    try:
        waypoint_index = int(waypoint_index)
    except (TypeError, ValueError):
        waypoint_index = 0
    waypoint_index = max(
        0,
        waypoint_index
    )
    # --------------------------------------------------------
    # Normalize heading
    # --------------------------------------------------------
    heading = normalize_heading(heading)
    # --------------------------------------------------------
    # Get next progressive waypoint
    # --------------------------------------------------------
    next_point, updated_index = get_next_waypoint(
        current_coords,
        points,
        waypoint_index
    )
    # --------------------------------------------------------
    # Route completed
    # --------------------------------------------------------
    if next_point is None:
        return {
            "command": "STOP",
            "waypoint_index": updated_index,
            "route_complete": True,
            "target_waypoint": None,
            "distance_to_target": 0.0,
            "desired_bearing": None,
            "angle_error": None
        }
    # --------------------------------------------------------
    # Calculate desired bearing
    # --------------------------------------------------------
    desired_bearing = calculate_bearing(
        current_coords,
        next_point
    )
    # --------------------------------------------------------
    # Calculate heading error
    # --------------------------------------------------------
    angle_error = angle_difference(
        desired_bearing,
        heading
    )
    # --------------------------------------------------------
    # Generate movement command
    # --------------------------------------------------------
    command = generate_command(
        angle_error
    )
    # --------------------------------------------------------
    # Distance to current target
    # --------------------------------------------------------
    distance_to_target = calculate_distance(
        to_tuple(current_coords),
        to_tuple(next_point)
    )
    # --------------------------------------------------------
    # Return complete navigation state
    # --------------------------------------------------------
    return {
        "command": command,
        "waypoint_index": updated_index,
        "route_complete": False,
        "target_waypoint": next_point,
        "distance_to_target": round(
            distance_to_target,
            2
        ),
        "desired_bearing": round(
            desired_bearing,
            2
        ),
        "angle_error": round(
            angle_error,
            2
        )
    }