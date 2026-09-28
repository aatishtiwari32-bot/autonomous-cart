"""
NAVIGATION API / NAVIGATION CONTROLLER

This is a normal Python module.

IMPORTANT
---------
There is NO FastAPI app in this file.

FastAPI endpoints belong to the actual API layer.
This module contains the navigation decision logic.

Responsibilities
----------------

1. Receive the authenticated command stored by the
   User Dashboard API.

2. Read the user's selected navigation mode:

       google
       self
       manual

3. Handle the complete mission sequence:

       KART CURRENT LOCATION
               ↓
          USER LOCATION
               ↓
        DELIVERY POINT
               ↓
         FINAL LOCATION

4. For autonomous navigation, give the pipeline only:

       current kart coordinates
       target coordinates
       heading
       navigation mode

5. For manual control, directly return the manual
   command received from the dashboard.

The final location can be ANY valid GPS coordinate.
It does not have to be the user's original location.
"""


from dataclasses import dataclass
from threading import Lock
from typing import Optional

from navigation.pipeline import pipeline

from navigation.navigation_tools.fnpp import (
    calculate_distance,
    to_tuple,
)

from all_api.user_dashboard_api import (
    get_command as get_dashboard_command,
)


# ============================================================
# CONFIGURATION
# ============================================================

# Distance within which a mission target is considered
# reached.

ARRIVAL_THRESHOLD = 7.0  # metres


# ------------------------------------------------------------
# Navigation modes
# ------------------------------------------------------------

GOOGLE_ROUTE = "google"
SELF_ROUTE = "self"
MANUAL_CONTROL = "manual"


ALLOWED_NAVIGATION_MODES = {
    GOOGLE_ROUTE,
    SELF_ROUTE,
    MANUAL_CONTROL,
}


# ------------------------------------------------------------
# Pipeline routing values
#
# These are used only when calling pipeline().
#
# Google = 0
# Self   = 1
# ------------------------------------------------------------

PIPELINE_GOOGLE_ROUTE = 0
PIPELINE_SELF_ROUTE = 1


# ------------------------------------------------------------
# Safe command
# ------------------------------------------------------------

SAFE_STOP_COMMAND = "STOP"


# ------------------------------------------------------------
# Manual commands
# ------------------------------------------------------------

ALLOWED_MANUAL_COMMANDS = {
    "F",
    "SR",
    "SL",
    "R",
    "L",
    "STOP",
}


# ============================================================
# MISSION PHASES
# ============================================================

TO_USER = "TO_USER"
TO_DELIVERY = "TO_DELIVERY"
TO_FINAL = "TO_FINAL"
COMPLETE = "COMPLETE"


# ============================================================
# PER-KART NAVIGATION STATE
# ============================================================

@dataclass
class NavigationState:
    """
    Runtime state for one kart.

    The user dashboard gives us three fixed destinations:

        user
        delivery
        final

    The kart's current position changes continuously,
    so kart coordinates are deliberately NOT part of the
    mission signature.
    """

    # --------------------------------------------------------
    # Mission identification
    # --------------------------------------------------------

    mission_key: Optional[tuple] = None

    # --------------------------------------------------------
    # Current mission phase
    # --------------------------------------------------------

    phase: str = TO_USER

    # --------------------------------------------------------
    # Last known navigation mode
    # --------------------------------------------------------

    navigation_mode: Optional[str] = None

    # --------------------------------------------------------
    # Last command generated
    # --------------------------------------------------------

    last_command: str = SAFE_STOP_COMMAND


# ============================================================
# GLOBAL RUNTIME STATE
# ============================================================

# One NavigationState per kart.

navigation_states = {}


# Protects navigation_states from concurrent requests.

state_lock = Lock()


# ============================================================
# COORDINATE HELPERS
# ============================================================

def _mission_key(
    user_coords,
    delivery_point,
    final_location,
):
    """
    Create a stable mission identifier.

    Navigation mode is intentionally NOT included.

    Why?

    Because changing:

        google → self

    must NOT restart the robot from the USER location.

    It should continue the current mission from its current
    phase.
    """

    user_point = to_tuple(
        user_coords
    )

    delivery_point_value = to_tuple(
        delivery_point
    )

    final_point = to_tuple(
        final_location
    )

    return (
        round(
            user_point[0],
            7
        ),
        round(
            user_point[1],
            7
        ),

        round(
            delivery_point_value[0],
            7
        ),
        round(
            delivery_point_value[1],
            7
        ),

        round(
            final_point[0],
            7
        ),
        round(
            final_point[1],
            7
        ),
    )


# ============================================================
# DISTANCE
# ============================================================

def _distance_to_target(
    current_coords,
    target_coords,
):
    """
    Return distance between kart and target in metres.
    """

    current_point = to_tuple(
        current_coords
    )

    target_point = to_tuple(
        target_coords
    )

    return calculate_distance(
        current_point,
        target_point
    )


# ============================================================
# TARGET RESOLUTION
# ============================================================

def _get_target_for_phase(
    phase,
    user_coords,
    delivery_point,
    final_location,
):
    """
    Return the target location corresponding to the
    current mission phase.
    """

    if phase == TO_USER:

        return user_coords

    if phase == TO_DELIVERY:

        return delivery_point

    if phase == TO_FINAL:

        return final_location

    return None


# ============================================================
# MISSION STATE INITIALIZATION
# ============================================================

def _get_or_create_state(
    kart_id,
    user_coords,
    delivery_point,
    final_location,
):
    """
    Get the current navigation state for a kart.

    If the dashboard has supplied a completely new mission,
    start from the USER location.
    """

    mission_key = _mission_key(
        user_coords,
        delivery_point,
        final_location,
    )

    with state_lock:

        current_state = navigation_states.get(
            kart_id
        )

        # ----------------------------------------------------
        # No previous mission
        # ----------------------------------------------------

        if current_state is None:

            current_state = NavigationState(
                mission_key=mission_key,
                phase=TO_USER,
            )

            navigation_states[
                kart_id
            ] = current_state

            return current_state

        # ----------------------------------------------------
        # New mission
        # ----------------------------------------------------

        if current_state.mission_key != mission_key:

            current_state = NavigationState(
                mission_key=mission_key,
                phase=TO_USER,
            )

            navigation_states[
                kart_id
            ] = current_state

        return current_state


# ============================================================
# TARGET PROGRESSION
# ============================================================

def _advance_reached_targets(
    current_state,
    current_coords,
    user_coords,
    delivery_point,
    final_location,
):
    """
    Advance the mission when the current target has been
    reached.

    This function can advance through more than one phase
    in a single call.

    Example:

        kart already at USER
               ↓
        immediately TO_DELIVERY

    Or:

        user == delivery == final
               ↓
        COMPLETE
    """

    # --------------------------------------------------------
    # Maximum of three mission legs.
    #
    # The loop is intentionally bounded for safety.
    # --------------------------------------------------------

    for _ in range(3):

        if current_state.phase == COMPLETE:

            return

        target = _get_target_for_phase(
            current_state.phase,
            user_coords,
            delivery_point,
            final_location,
        )

        if target is None:

            current_state.phase = COMPLETE

            return

        try:

            distance = _distance_to_target(
                current_coords,
                target,
            )

        except (
            TypeError,
            ValueError,
        ):

            return

        # ----------------------------------------------------
        # Target not reached yet
        # ----------------------------------------------------

        if distance > ARRIVAL_THRESHOLD:

            return

        # ----------------------------------------------------
        # USER reached
        # ----------------------------------------------------

        if current_state.phase == TO_USER:

            current_state.phase = TO_DELIVERY

            continue

        # ----------------------------------------------------
        # DELIVERY reached
        # ----------------------------------------------------

        if current_state.phase == TO_DELIVERY:

            current_state.phase = TO_FINAL

            continue

        # ----------------------------------------------------
        # FINAL location reached
        # ----------------------------------------------------

        if current_state.phase == TO_FINAL:

            current_state.phase = COMPLETE

            continue


# ============================================================
# MANUAL COMMAND
# ============================================================

def _handle_manual_command(
    command_data,
):
    """
    Extract and validate the manual command from the
    User Dashboard API.

    Returns:
        valid command string

    Invalid input → STOP
    """

    manual_command = command_data.get(
        "manual_command"
    )

    if manual_command is None:

        return SAFE_STOP_COMMAND

    manual_command = str(
        manual_command
    ).strip().upper()

    if manual_command not in ALLOWED_MANUAL_COMMANDS:

        return SAFE_STOP_COMMAND

    return manual_command


# ============================================================
# AUTONOMOUS MODE
# ============================================================

def _handle_autonomous_navigation(
    kart_id,
    current_coords,
    heading,
    command_data,
):
    """
    Handle Google or Self autonomous navigation.

    Navigation API determines:

        - current mission phase
        - current target
        - Google / Self mode

    Pipeline determines the actual driving command.

    Pipeline receives only:

        current coordinates
        target coordinates
        heading
        route mode
    """

    # --------------------------------------------------------
    # Extract mission coordinates
    # --------------------------------------------------------

    user_coords = command_data.get(
        "user_coords"
    )

    delivery_point = command_data.get(
        "delivery_point"
    )

    final_location = command_data.get(
        "final_location"
    )

    # --------------------------------------------------------
    # Validate that all three destinations exist
    # --------------------------------------------------------

    if (
        user_coords is None
        or delivery_point is None
        or final_location is None
    ):

        return SAFE_STOP_COMMAND

    # --------------------------------------------------------
    # Get mission state
    # --------------------------------------------------------

    current_state = _get_or_create_state(
        kart_id=kart_id,
        user_coords=user_coords,
        delivery_point=delivery_point,
        final_location=final_location,
    )

    # --------------------------------------------------------
    # Check whether current target has already been reached.
    #
    # This is handled BEFORE calling pipeline().
    # --------------------------------------------------------

    _advance_reached_targets(
        current_state=current_state,
        current_coords=current_coords,
        user_coords=user_coords,
        delivery_point=delivery_point,
        final_location=final_location,
    )

    # --------------------------------------------------------
    # Mission finished
    # --------------------------------------------------------

    if current_state.phase == COMPLETE:

        with state_lock:

            current_state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND

    # --------------------------------------------------------
    # Determine target
    # --------------------------------------------------------

    target = _get_target_for_phase(
        current_state.phase,
        user_coords,
        delivery_point,
        final_location,
    )

    if target is None:

        with state_lock:

            current_state.phase = COMPLETE
            current_state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND

    # --------------------------------------------------------
    # Determine route mode selected by USER
    # --------------------------------------------------------

    navigation_mode = str(
        command_data.get(
            "navigation_mode",
            ""
        )
    ).strip().lower()

    # --------------------------------------------------------
    # Convert dashboard choice into pipeline route mode
    # --------------------------------------------------------

    if navigation_mode == SELF_ROUTE:

        pipeline_route_mode = (
            PIPELINE_SELF_ROUTE
        )

    elif navigation_mode == GOOGLE_ROUTE:

        pipeline_route_mode = (
            PIPELINE_GOOGLE_ROUTE
        )

    else:

        with state_lock:

            current_state.last_command = (
                SAFE_STOP_COMMAND
            )

        return SAFE_STOP_COMMAND

    # --------------------------------------------------------
    # Call the autonomous driving engine.
    #
    # IMPORTANT:
    #
    # No marketplace
    # No delivery phase
    # No final mission logic
    #
    # Pipeline only gets the current leg.
    # --------------------------------------------------------

    try:

        command = pipeline(
            current_coords,
            target,
            heading,
            pipeline_route_mode,
        )

    except Exception:

        # Navigation engine failure.
        # Safe behaviour = STOP.

        command = SAFE_STOP_COMMAND

    # --------------------------------------------------------
    # Validate pipeline command
    # --------------------------------------------------------

    command = str(
        command
    ).strip().upper()

    if command not in {
        "F",
        "SR",
        "SL",
        "R",
        "L",
        "STOP",
    }:

        command = SAFE_STOP_COMMAND

    # --------------------------------------------------------
    # Save runtime state
    # --------------------------------------------------------

    with state_lock:

        current_state.navigation_mode = (
            navigation_mode
        )

        current_state.last_command = command

    return command


# ============================================================
# MAIN NAVIGATION FUNCTION
# ============================================================

def get_navigation_command(
    kart_id,
    kart_coords,
    heading,
):
    """
    Main navigation controller.

    Parameters
    ----------
    kart_id:
        Identifier of the authenticated kart.

    kart_coords:
        CURRENT GPS position of the kart.

        This is obtained from the kart itself.

    heading:
        Current kart heading.

    Returns
    -------
    str

        Autonomous:
            F / SR / SL / R / L / STOP

        Manual:
            dashboard-selected command
    """

    # ========================================================
    # BASIC KART ID VALIDATION
    # ========================================================

    if not kart_id:

        return SAFE_STOP_COMMAND

    kart_id = str(
        kart_id
    ).strip()

    if not kart_id:

        return SAFE_STOP_COMMAND

    # ========================================================
    # VALIDATE CURRENT KART COORDINATES
    # ========================================================

    try:

        to_tuple(
            kart_coords
        )
    except (
        TypeError,
        ValueError,
    ):
        return SAFE_STOP_COMMAND
    # ========================================================
    # READ DASHBOARD COMMAND
    # ========================================================
    try:
        dashboard_response = (
            get_dashboard_command(
                kart_id
            )
        )
    except Exception:
        return SAFE_STOP_COMMAND
    if not isinstance(
        dashboard_response,
        dict,
    ):
        return SAFE_STOP_COMMAND
    command_data = (
        dashboard_response.get(
            "command"
        )
    )
    if not isinstance(
        command_data,
        dict,
    ):
        return SAFE_STOP_COMMAND
    # ========================================================
    # READ NAVIGATION MODE
    # ========================================================
    navigation_mode = str(
        command_data.get(
            "navigation_mode",
            ""
        )
    ).strip().lower()
    # ========================================================
    # MANUAL MODE
    # ========================================================
    if navigation_mode == MANUAL_CONTROL:
        command = _handle_manual_command(
            command_data
        )
        return command
    # ========================================================
    # AUTONOMOUS MODE
    # ========================================================
    if navigation_mode in {
        GOOGLE_ROUTE,
        SELF_ROUTE,
    }:
        return _handle_autonomous_navigation(
            kart_id=kart_id,
            current_coords=kart_coords,
            heading=heading,
            command_data=command_data,
        )
    # ========================================================
    # UNKNOWN MODE
    # ========================================================
    return SAFE_STOP_COMMAND
# ============================================================
# NAVIGATION STATUS
# ============================================================
def get_navigation_status(
    kart_id,
):
    """
    Return navigation state for dashboard/telemetry use.
    This does NOT control the kart.
    """
    kart_id = str(
        kart_id
    ).strip()
    with state_lock:
        current_state = navigation_states.get(
            kart_id
        )
        if current_state is None:
            return {
                "kart_id": kart_id,
                "phase": "IDLE",
                "navigation_mode": None,
                "last_command": SAFE_STOP_COMMAND,
            }
        return {
            "kart_id": kart_id,
            "phase": current_state.phase,
            "navigation_mode": (
                current_state.navigation_mode
            ),
            "last_command": (
                current_state.last_command
            ),
        }
# ============================================================
# RESET KART NAVIGATION
# ============================================================
def reset_navigation(
    kart_id,
):
    """
    Reset navigation state for one kart.

    Useful when:
        - a mission is cancelled
        - a new mission must start explicitly
        - kart is being reset
    """
    kart_id = str(
        kart_id
    ).strip()

    with state_lock:

        navigation_states.pop(
            kart_id,
            None
        )