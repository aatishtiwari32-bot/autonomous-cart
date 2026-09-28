"""
AUTONOMOUS DRIVING PIPELINE

Responsibility
--------------

This module establishes autonomous driving between ONLY:

    CURRENT KART LOCATION
            ↓
        TARGET LOCATION

The higher-level Navigation API is responsible for deciding
which target the kart should currently travel toward.

For example:

    Kart
      ↓
    User
      ↓
    Delivery
      ↓
    Final

But pipeline knows nothing about this sequence.

Pipeline only receives:

    current_coords
    target_coords
    heading
    routing_mode

Routing mode:

    0 -> Google Routes
    1 -> Self / JUET graph

Manual control is NOT handled here.

The Navigation API handles manual commands directly.
"""


import os

from dataclasses import dataclass, field
from threading import Lock
from typing import Optional


# ============================================================
# GOOGLE NAVIGATION
# ============================================================

from .api_navigation.create_path import (
    get_google_route,
)

from .api_navigation.decode_route import (
    extract_route_points,
)


# ============================================================
# AUTONOMOUS NAVIGATION
# ============================================================

from .navigation_tools.navigate import (
    navigate,
)

from .navigation_tools.movement import (
    movement,
)

from .navigation_tools.fnpp import (
    calculate_distance,
    to_tuple,
)


# ============================================================
# SELF NAVIGATION
# ============================================================

from .self_navigation.shortest_distance import (
    short_distance,
)

from .self_navigation.polyline_extraction import (
    extract_polyline,
)


# ============================================================
# CAMERA
# ============================================================

from other_tools.frame_extraction import (
    get_frame,
)


# ============================================================
# CONFIGURATION
# ============================================================


# ------------------------------------------------------------
# Destination arrival threshold
# ------------------------------------------------------------

ARRIVAL_THRESHOLD = 7.0


# ------------------------------------------------------------
# Waypoint route modes
# ------------------------------------------------------------

GOOGLE_ROUTE = 0
SELF_ROUTE = 1


# ------------------------------------------------------------
# Safe command
# ------------------------------------------------------------

SAFE_STOP_COMMAND = "STOP"


# ------------------------------------------------------------
# Allowed final commands
# ------------------------------------------------------------

ALLOWED_COMMANDS = {
    "F",
    "SR",
    "SL",
    "R",
    "L",
    "STOP",
}


# ------------------------------------------------------------
# Camera source
# ------------------------------------------------------------
#
# Examples:
#
# USB camera:
#     CAMERA_SOURCE=0
#
# IP camera:
#     CAMERA_SOURCE=http://192.168.1.50:8080/video
#
# RTSP:
#     CAMERA_SOURCE=rtsp://...
#
# ------------------------------------------------------------

CAMERA_SOURCE = os.getenv(
    "CAMERA_SOURCE",
    "0",
)


# ------------------------------------------------------------
# Pothole detection
# ------------------------------------------------------------
#
# Pothole detector is enabled automatically when:
#
#     POTHOLE_DETECTION_ENABLED=true
#
# Otherwise it remains disabled.
#
# This prevents a missing pothole model from crashing the
# complete autonomous navigation pipeline during development.
#
# ------------------------------------------------------------

POTHOLE_DETECTION_ENABLED = (
    os.getenv(
        "POTHOLE_DETECTION_ENABLED",
        "false",
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)


# ============================================================
# PIPELINE STATE
# ============================================================

@dataclass
class PipelineState:
    """
    State of the current autonomous route.

    There is intentionally NO:

        user/delivery/final

    mission logic here.

    Only one current route is maintained:

        current position -> target
    """

    # --------------------------------------------------------
    # Route identity
    # --------------------------------------------------------

    route_key: Optional[tuple] = None


    # --------------------------------------------------------
    # Cached route points
    # --------------------------------------------------------

    route_points: list = field(
        default_factory=list
    )


    # --------------------------------------------------------
    # Current waypoint index
    # --------------------------------------------------------

    waypoint_index: int = 0


    # --------------------------------------------------------
    # Last selected route mode
    # --------------------------------------------------------

    routing_mode: Optional[int] = None


    # --------------------------------------------------------
    # Last command
    # --------------------------------------------------------

    last_command: str = SAFE_STOP_COMMAND


    # --------------------------------------------------------
    # Last error
    # --------------------------------------------------------

    last_error: Optional[str] = None


# ------------------------------------------------------------
# Single-kart prototype state
# ------------------------------------------------------------

state = PipelineState()


# ------------------------------------------------------------
# Thread protection
# ------------------------------------------------------------

state_lock = Lock()


# ============================================================
# COMMAND HELPERS
# ============================================================

def _normalize_command(
    command,
):
    """
    Convert a generated command into one of the project's
    allowed commands.

    Unknown command -> STOP.
    """

    if command is None:

        return SAFE_STOP_COMMAND

    command = str(
        command
    ).strip().upper()

    if command not in ALLOWED_COMMANDS:

        return SAFE_STOP_COMMAND

    return command


# ============================================================
# ROUTE MODE NORMALIZATION
# ============================================================

def _normalize_routing_mode(
    routing_mode,
):
    """
    Normalize routing mode.

    Supported:

        0
        "0"
        "google"

        1
        "1"
        "self"
    """

    if isinstance(
        routing_mode,
        str,
    ):

        value = (
            routing_mode
            .strip()
            .lower()
        )

        if value in {
            "google",
            "0",
        }:

            return GOOGLE_ROUTE

        if value in {
            "self",
            "1",
        }:

            return SELF_ROUTE

        return None

    try:

        value = int(
            routing_mode
        )

    except (
        TypeError,
        ValueError,
    ):

        return None

    if value in {
        GOOGLE_ROUTE,
        SELF_ROUTE,
    }:

        return value

    return None


# ============================================================
# CAMERA SOURCE
# ============================================================

def _resolve_camera_source(
    source,
):
    """
    Convert numeric camera source strings into integer
    indexes.

    Example:

        "0" -> 0
        "1" -> 1

    URLs remain strings.
    """

    if isinstance(
        source,
        str,
    ):

        value = source.strip()

        if value.isdigit():

            return int(
                value
            )

        return value

    return source


# ============================================================
# CAMERA FRAME
# ============================================================

def _get_camera_frame():
    """
    Capture one camera frame.

    Camera errors never result in a fake "clear path".

    None is returned and the caller will safely STOP.
    """

    source = _resolve_camera_source(
        CAMERA_SOURCE
    )

    try:

        return get_frame(
            source
        )

    except Exception:

        return None


# ============================================================
# GOOGLE ROUTE
# ============================================================

def _build_google_route(
    current_coords,
    target_coords,
):
    """
    Build a GPS waypoint route using Google Routes API.

    No fallback to self-routing is performed here.

    The user selected the routing mode, so:

        Google selected
            ↓
        Google failure
            ↓
        STOP

    """

    try:

        route_response = get_google_route(
            current_coords,
            target_coords,
        )

    except Exception as error:

        with state_lock:

            state.last_error = (
                f"Google route error: {error}"
            )

        return []

    if not route_response:

        with state_lock:

            state.last_error = (
                "Google route was not returned."
            )

        return []

    try:

        points = extract_route_points(
            route_response
        )

    except Exception as error:

        with state_lock:

            state.last_error = (
                f"Google polyline decode error: {error}"
            )

        return []

    if not points:

        with state_lock:

            state.last_error = (
                "Google route contained no usable points."
            )

        return []

    return points


# ============================================================
# SELF ROUTE
# ============================================================

def _build_self_route(
    current_coords,
    target_coords,
):
    """
    Build a GPS waypoint route using the JUET self-routing
    graph.

    Flow:

        current GPS
             ↓
        closest graph vertex
             ↓
        shortest graph path
             ↓
        stored polyline
             ↓
        GPS waypoints
    """

    try:

        route_result = short_distance(
            current_coords,
            target_coords,
        )

    except Exception as error:

        with state_lock:

            state.last_error = (
                f"Self route search error: {error}"
            )

        return []

    if not route_result:

        with state_lock:

            state.last_error = (
                "Self route could not be created."
            )

        return []

    try:

        points = extract_polyline(
            route_result
        )

    except Exception as error:

        with state_lock:

            state.last_error = (
                f"Self route polyline error: {error}"
            )

        return []

    if not points:

        with state_lock:

            state.last_error = (
                "Self route contained no usable points."
            )

        return []

    return points


# ============================================================
# ROUTE BUILDER
# ============================================================

def _build_route(
    current_coords,
    target_coords,
    routing_mode,
):
    """
    Build exactly ONE route:

        current -> target

    according to the routing mode chosen by the user.
    """

    if routing_mode == GOOGLE_ROUTE:

        return _build_google_route(
            current_coords,
            target_coords,
        )

    if routing_mode == SELF_ROUTE:

        return _build_self_route(
            current_coords,
            target_coords,
        )

    return []


# ============================================================
# ROUTE KEY
# ============================================================

def _create_route_key(
    target_coords,
    routing_mode,
):
    """
    Create an identity for the current route.

    Current kart coordinates are intentionally NOT included.

    The kart moves continuously, so putting current position
    into the key would rebuild the route on every call.
    """

    latitude, longitude = to_tuple(
        target_coords
    )

    return (
        round(
            latitude,
            7,
        ),
        round(
            longitude,
            7,
        ),
        int(
            routing_mode
        ),
    )


# ============================================================
# ROUTE INITIALIZATION
# ============================================================

def _ensure_route(
    current_coords,
    target_coords,
    routing_mode,
):
    """
    Build a new route only when the current target or routing
    mode changes.

    Otherwise continue using the cached route and existing
    waypoint index.
    """

    route_key = _create_route_key(
        target_coords,
        routing_mode,
    )

    with state_lock:

        route_already_exists = (
            state.route_key == route_key
            and bool(
                state.route_points
            )
            and state.routing_mode == routing_mode
        )

    if route_already_exists:

        return True


    # --------------------------------------------------------
    # New route
    # --------------------------------------------------------

    route_points = _build_route(
        current_coords,
        target_coords,
        routing_mode,
    )

    if not route_points:

        with state_lock:

            state.route_key = route_key
            state.route_points = []
            state.waypoint_index = 0
            state.routing_mode = routing_mode
            state.last_command = (
                SAFE_STOP_COMMAND
            )

        return False


    with state_lock:

        state.route_key = route_key

        state.route_points = (
            route_points
        )

        state.waypoint_index = 0

        state.routing_mode = routing_mode

        state.last_error = None

        state.last_command = (
            SAFE_STOP_COMMAND
        )

    return True


# ============================================================
# OBSTACLE DETECTION
# ============================================================

def _detect_obstacle(
    frame,
):
    """
    Run the normal YOLO obstacle detector.

    Returns the detector result.

    On detector failure, returns a STOP result.
    """

    try:

        result = movement(
            frame
        )

    except Exception as error:

        return {
            "obstacle_present": True,
            "side": "CENTER",
            "command": "STOP",
            "obstacle_class": "detector_error",
            "confidence": 1.0,
            "danger_score": 1.0,
            "error": str(error),
        }

    if not isinstance(
        result,
        dict,
    ):

        return {
            "obstacle_present": True,
            "side": "CENTER",
            "command": "STOP",
            "obstacle_class": "invalid_detector_result",
            "confidence": 1.0,
            "danger_score": 1.0,
        }

    return result


# ============================================================
# POTHOLE DETECTION
# ============================================================

def _detect_pothole(
    frame,
):
    """
    Run the optional pothole detector.

    The existing pothole detector uses a separate trained
    model.

    If pothole detection is disabled, no pothole is reported.

    If enabled but the detector cannot be loaded/executed,
    STOP is returned for safety.
    """

    if not POTHOLE_DETECTION_ENABLED:

        return {
            "pothole_present": False,
            "side": None,
            "command": None,
        }


    # --------------------------------------------------------
    # Lazy import
    # --------------------------------------------------------
    #
    # This prevents the pothole model from being loaded merely
    # because pipeline.py was imported.
    #

    try:

        from .navigation_tools.pothole_detection import (
            detect_pothole,
        )

    except Exception as error:

        return {
            "pothole_present": True,
            "side": "CENTER",
            "command": "STOP",
            "error": (
                f"Pothole detector unavailable: {error}"
            ),
        }


    # --------------------------------------------------------
    # Detector call
    # --------------------------------------------------------

    try:

        result = detect_pothole(
            frame
        )

    except Exception as error:

        return {
            "pothole_present": True,
            "side": "CENTER",
            "command": "STOP",
            "error": (
                f"Pothole detector error: {error}"
            ),
        }


    if not isinstance(
        result,
        dict,
    ):

        return {
            "pothole_present": True,
            "side": "CENTER",
            "command": "STOP",
            "error": (
                "Invalid pothole detector result."
            ),
        }

    return result


# ============================================================
# SAFETY ARBITRATION
# ============================================================

def _safety_command(
    obstacle_result,
    pothole_result,
):
    """
    Combine obstacle and pothole detector outputs.

    Safety rules:

        CENTER obstacle → STOP
        CENTER pothole  → STOP

        LEFT only        → SR
        RIGHT only       → SL

        Conflicting detections → STOP

    The vision system has priority over navigation.
    """

    obstacle_present = bool(
        obstacle_result.get(
            "obstacle_present",
            False,
        )
    )

    pothole_present = bool(
        pothole_result.get(
            "pothole_present",
            False,
        )
    )


    # ========================================================
    # NOTHING DETECTED
    # ========================================================

    if (
        not obstacle_present
        and not pothole_present
    ):

        return None


    # ========================================================
    # COLLECT SIDES
    # ========================================================

    sides = []

    if obstacle_present:

        obstacle_side = str(
            obstacle_result.get(
                "side",
                "CENTER",
            )
        ).upper()

        sides.append(
            obstacle_side
        )


    if pothole_present:

        pothole_side = str(
            pothole_result.get(
                "side",
                "CENTER",
            )
        ).upper()

        sides.append(
            pothole_side
        )


    # ========================================================
    # ANY CENTER HAZARD
    # ========================================================

    if "CENTER" in sides:

        return SAFE_STOP_COMMAND


    # ========================================================
    # CONFLICTING SIDES
    # ========================================================

    unique_sides = set(
        sides
    )

    if (
        "LEFT" in unique_sides
        and
        "RIGHT" in unique_sides
    ):

        return SAFE_STOP_COMMAND


    # ========================================================
    # ONLY LEFT
    # ========================================================

    if unique_sides == {
        "LEFT"
    }:

        return "SR"


    # ========================================================
    # ONLY RIGHT
    # ========================================================

    if unique_sides == {
        "RIGHT"
    }:

        return "SL"


    # ========================================================
    # UNKNOWN SAFETY STATE
    # ========================================================

    return SAFE_STOP_COMMAND


# ============================================================
# DESTINATION ARRIVAL
# ============================================================

def _has_reached_target(
    current_coords,
    target_coords,
):
    """
    Check whether the kart is within the 7m destination
    threshold.
    """

    try:

        current_point = to_tuple(
            current_coords
        )

        target_point = to_tuple(
            target_coords
        )

        distance = calculate_distance(
            current_point,
            target_point,
        )

    except (
        TypeError,
        ValueError,
    ):

        return False


    return (
        distance
        <= ARRIVAL_THRESHOLD
    )


# ============================================================
# ROUTE RESET
# ============================================================

def reset_pipeline():
    """
    Clear the current route and waypoint progress.

    Navigation API can call this when a mission is cancelled
    or when a completely fresh route must be established.
    """

    global state

    with state_lock:

        state = PipelineState()


# ============================================================
# PIPELINE STATE
# ============================================================

def get_pipeline_state():
    """
    Return the current autonomous driving state.

    Useful later for telemetry/dashboard.
    """

    with state_lock:

        return {
            "route_active": bool(
                state.route_points
            ),
            "routing_mode": (
                state.routing_mode
            ),
            "waypoint_index": (
                state.waypoint_index
            ),
            "route_points_count": len(
                state.route_points
            ),
            "last_command": (
                state.last_command
            ),
            "last_error": (
                state.last_error
            ),
        }


# ============================================================
# MAIN AUTONOMOUS PIPELINE
# ============================================================

def pipeline(
    current_coords,
    target_coords,
    heading,
    routing_mode,
):
    """
    Establish autonomous driving between:

        CURRENT KART LOCATION
                  ↓
             TARGET LOCATION

    Parameters
    ----------
    current_coords:
        Current kart GPS position.

    target_coords:
        Current target GPS position.

    heading:
        Current kart heading from IMU/compass.

    routing_mode:
        0 -> Google
        1 -> Self

    Returns
    -------
    str

        F
        SR
        SL
        R
        L
        STOP
    """

    # ========================================================
    # VALIDATE CURRENT COORDINATES
    # ========================================================

    try:

        to_tuple(
            current_coords
        )

    except (
        TypeError,
        ValueError,
    ) as error:

        with state_lock:

            state.last_error = (
                f"Invalid current coordinates: {error}"
            )

            state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND


    # ========================================================
    # VALIDATE TARGET COORDINATES
    # ========================================================

    try:

        to_tuple(
            target_coords
        )

    except (
        TypeError,
        ValueError,
    ) as error:

        with state_lock:

            state.last_error = (
                f"Invalid target coordinates: {error}"
            )

            state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND


    # ========================================================
    # NORMALIZE ROUTING MODE
    # ========================================================

    routing_mode = _normalize_routing_mode(
        routing_mode
    )

    if routing_mode is None:

        with state_lock:

            state.last_error = (
                "Invalid routing mode."
            )

            state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND


    # ========================================================
    # CAMERA
    # ========================================================
    #
    # Camera failure is treated as unsafe because the
    # obstacle-detection layer cannot verify the path.
    #

    frame = _get_camera_frame()

    if frame is None:

        with state_lock:

            state.last_error = (
                "Camera frame unavailable."
            )

            state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND


    # ========================================================
    # OBSTACLE DETECTION
    # ========================================================

    obstacle_result = _detect_obstacle(
        frame
    )


    # ========================================================
    # POTHOLE DETECTION
    # ========================================================

    pothole_result = _detect_pothole(
        frame
    )


    # ========================================================
    # SAFETY PRIORITY
    # ========================================================

    safety_command = _safety_command(
        obstacle_result,
        pothole_result,
    )

    if safety_command is not None:

        with state_lock:

            state.last_command = (
                safety_command
            )

            # Store any detector error for telemetry/debugging.

            detector_error = (
                obstacle_result.get(
                    "error"
                )
                or
                pothole_result.get(
                    "error"
                )
            )

            if detector_error:

                state.last_error = (
                    str(
                        detector_error
                    )
                )

        return safety_command


    # ========================================================
    # DESTINATION REACHED
    # ========================================================

    if _has_reached_target(
        current_coords,
        target_coords,
    ):

        with state_lock:

            state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND


    # ========================================================
    # BUILD / REUSE ROUTE
    # ========================================================

    route_ready = _ensure_route(
        current_coords,
        target_coords,
        routing_mode,
    )

    if not route_ready:

        with state_lock:

            state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND


    # ========================================================
    # GET CURRENT ROUTE STATE
    # ========================================================

    with state_lock:

        route_points = list(
            state.route_points
        )

        waypoint_index = (
            state.waypoint_index
        )


    # ========================================================
    # AUTONOMOUS NAVIGATION
    # ========================================================
    try:
        navigation_result = navigate(
            heading=heading,
            current_coords=current_coords,
            points=route_points,
            waypoint_index=waypoint_index,
        )
    except Exception as error:
        with state_lock:
            state.last_error = (
                f"Navigation error: {error}"
            )
            state.last_command = (
                SAFE_STOP_COMMAND
            )
        return SAFE_STOP_COMMAND
    # ========================================================
    # UPDATE WAYPOINT PROGRESS
    # ========================================================
    new_waypoint_index = navigation_result.get(
        "waypoint_index",
        waypoint_index,
    )
    try:
        new_waypoint_index = int(
            new_waypoint_index
        )
    except (
        TypeError,
        ValueError,
    ):
        new_waypoint_index = (
            waypoint_index
        )
    # ========================================================
    # ROUTE COMPLETE
    # ========================================================
    route_complete = bool(
        navigation_result.get(
            "route_complete",
            False,
        )
    )
    if route_complete:
        with state_lock:
            state.waypoint_index = (
                new_waypoint_index
            )
            state.last_command = (
                SAFE_STOP_COMMAND
            )
        return SAFE_STOP_COMMAND
    # ========================================================
    # COMMAND
    # ========================================================
    command = _normalize_command(
        navigation_result.get(
            "command",
            SAFE_STOP_COMMAND,
        )
    )
    # ========================================================
    # SAVE STATE
    # ========================================================
    with state_lock:
        state.waypoint_index = (
            new_waypoint_index
        )
        state.last_command = command
    return command