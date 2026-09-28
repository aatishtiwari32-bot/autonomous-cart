"""
USER DASHBOARD API

Responsibility
--------------
1. Authenticate a kart.
2. Accept mission information from frontend.
3. Accept user's navigation-mode selection:
       - google
       - self
       - manual
4. Accept manual driving commands when manual mode is selected.
5. Store the currently active command/mission.
6. Provide the Navigation API with a clean command payload.

IMPORTANT
---------
The kart's CURRENT GPS coordinates are NOT received from the
user dashboard.

Kart current location will come separately from the kart/
telemetry side.

Mission coordinate flow:

    KART CURRENT LOCATION
            ↓
       USER LOCATION
            ↓
      DELIVERY POINT
            ↓
       FINAL LOCATION

The dashboard supplies only:

    user_coords
    delivery_point
    final_location

The user chooses:

    google
    self
    manual
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from threading import Lock
import os


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Autonomous Cart - User Dashboard API",
    version="1.0.0",
)


# ============================================================
# KART CREDENTIALS
# ============================================================
#
# Prototype:
#
#     kart_id = mark2
#     password = mark2
#
# For production, these must move to a database / secure
# authentication system.
#
# Environment variable supported:
#
#     KART_MARK2_PASSWORD
#
# Example Windows PowerShell:
#
#     $env:KART_MARK2_PASSWORD="your_password"
#

KART_CREDENTIALS = {
    "mark2": os.getenv(
        "KART_MARK2_PASSWORD",
        "mark2",
    ),
}


# ============================================================
# RUNTIME STATE
# ============================================================

# Authenticated kart IDs.

authenticated_karts = set()


# Current command/mission for each authenticated kart.

kart_commands = {}


# Thread safety for concurrent FastAPI requests.

state_lock = Lock()


# ============================================================
# CONSTANTS
# ============================================================

GOOGLE_ROUTE = "google"
SELF_ROUTE = "self"
MANUAL_CONTROL = "manual"

ALLOWED_MODES = {
    GOOGLE_ROUTE,
    SELF_ROUTE,
    MANUAL_CONTROL,
}

ALLOWED_MANUAL_COMMANDS = {
    "F",
    "SR",
    "SL",
    "R",
    "L",
    "STOP",
}


# ============================================================
# DATA MODELS
# ============================================================

class KartAuth(BaseModel):
    """
    Authentication information for a kart.
    """

    kart_id: str = Field(
        ...,
        min_length=1,
    )

    password: str = Field(
        ...,
        min_length=1,
    )


class Coordinates(BaseModel):
    """
    GPS coordinate.
    """

    latitude: float
    longitude: float


class KartCommand(BaseModel):
    """
    Complete command received from the user dashboard.

    The dashboard does NOT send current kart coordinates.

    The kart's current GPS position is obtained separately
    from the kart/telemetry system.

    The dashboard sends:

        user_coords
        delivery_point
        final_location

    and the user-selected mode:

        google
        self
        manual
    """

    navigation_mode: str

    user_coords: Coordinates

    delivery_point: Coordinates

    final_location: Coordinates

    # Required only when navigation_mode == "manual"
    manual_command: str | None = None


# ============================================================
# COORDINATE VALIDATION
# ============================================================

def _validate_coordinates(
    coordinates: Coordinates,
):
    """
    Validate latitude and longitude ranges.
    """

    if not (
        -90.0
        <= coordinates.latitude
        <= 90.0
    ):
        raise HTTPException(
            status_code=422,
            detail="Latitude must be between -90 and 90.",
        )

    if not (
        -180.0
        <= coordinates.longitude
        <= 180.0
    ):
        raise HTTPException(
            status_code=422,
            detail="Longitude must be between -180 and 180.",
        )


# ============================================================
# AUTHENTICATION HELPER
# ============================================================

def _require_authentication(
    kart_id: str,
):
    """
    Ensure that the kart has authenticated successfully.
    """

    with state_lock:

        authenticated = (
            kart_id in authenticated_karts
        )

    if not authenticated:

        raise HTTPException(
            status_code=401,
            detail="Kart is not authenticated.",
        )


# ============================================================
# KART AUTHENTICATION
# ============================================================

@app.post("/kart/auth")
def auth(
    auth_data: KartAuth,
):
    """
    Authenticate a kart.

    Request:

    {
        "kart_id": "mark2",
        "password": "mark2"
    }
    """

    kart_id = auth_data.kart_id.strip()

    expected_password = (
        KART_CREDENTIALS.get(kart_id)
    )

    if expected_password is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid kart ID or password.",
        )

    if auth_data.password != expected_password:

        raise HTTPException(
            status_code=401,
            detail="Invalid kart ID or password.",
        )

    with state_lock:

        authenticated_karts.add(
            kart_id
        )

    return {
        "authenticated": True,
        "kart_id": kart_id,
        "message": "Kart authentication successful.",
    }


# ============================================================
# RECEIVE COMMAND
# ============================================================

@app.post("/kart/command/{kart_id}")
def receive_command(
    kart_id: str,
    command: KartCommand,
):
    """
    Receive the user's selected navigation command.

    The user chooses the navigation mode.

    Example Google:

    {
        "navigation_mode": "google",
        "user_coords": {
            "latitude": 24.435455,
            "longitude": 77.162249
        },
        "delivery_point": {
            "latitude": 24.432049,
            "longitude": 77.161708
        },
        "final_location": {
            "latitude": 24.435455,
            "longitude": 77.162249
        }
    }

    Example Self:

    {
        "navigation_mode": "self",
        ...
    }

    Example Manual:

    {
        "navigation_mode": "manual",
        ...
        "manual_command": "F"
    }
    """

    kart_id = kart_id.strip()

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    _require_authentication(
        kart_id
    )

    # --------------------------------------------------------
    # Validate navigation mode
    # --------------------------------------------------------

    navigation_mode = (
        command.navigation_mode
        .strip()
        .lower()
    )

    if navigation_mode not in ALLOWED_MODES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid navigation mode. "
                "Allowed: google, self, manual."
            ),
        )

    # --------------------------------------------------------
    # Validate coordinates
    # --------------------------------------------------------

    _validate_coordinates(
        command.user_coords
    )

    _validate_coordinates(
        command.delivery_point
    )

    _validate_coordinates(
        command.final_location
    )

    # --------------------------------------------------------
    # Manual command validation
    # --------------------------------------------------------

    manual_command = None

    if navigation_mode == MANUAL_CONTROL:

        if command.manual_command is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "manual_command is required "
                    "when navigation_mode is 'manual'."
                ),
            )

        manual_command = (
            command.manual_command
            .strip()
            .upper()
        )

        if manual_command not in ALLOWED_MANUAL_COMMANDS:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid manual command. "
                    "Allowed: F, SR, SL, R, L, STOP."
                ),
            )

    # --------------------------------------------------------
    # Build clean command object
    # --------------------------------------------------------

    command_data = {
        "kart_id": kart_id,

        "navigation_mode": navigation_mode,

        "user_coords": {
            "latitude": command.user_coords.latitude,
            "longitude": command.user_coords.longitude,
        },

        "delivery_point": {
            "latitude": command.delivery_point.latitude,
            "longitude": command.delivery_point.longitude,
        },

        "final_location": {
            "latitude": command.final_location.latitude,
            "longitude": command.final_location.longitude,
        },

        "manual_command": manual_command,
    }

    # --------------------------------------------------------
    # Store latest command
    # --------------------------------------------------------

    with state_lock:

        kart_commands[
            kart_id
        ] = command_data

    return {
        "success": True,
        "message": "Command received successfully.",
        "command": command_data,
    }


# ============================================================
# GET CURRENT COMMAND
# ============================================================

@app.get("/kart/command/{kart_id}")
def get_command(
    kart_id: str,
):
    """
    Return the currently stored command.

    Navigation API will later consume this data.
    """

    kart_id = kart_id.strip()

    _require_authentication(
        kart_id
    )

    with state_lock:

        command = kart_commands.get(
            kart_id
        )

    if command is None:

        raise HTTPException(
            status_code=404,
            detail="No command has been configured for this kart.",
        )

    return {
        "success": True,
        "command": command,
    }


# ============================================================
# GET AUTHENTICATION STATUS
# ============================================================

@app.get("/kart/status/{kart_id}")
def kart_status(
    kart_id: str,
):
    """
    Return authentication and command status.
    """

    kart_id = kart_id.strip()

    with state_lock:

        authenticated = (
            kart_id
            in authenticated_karts
        )

        has_command = (
            kart_id
            in kart_commands
        )

    return {
        "kart_id": kart_id,
        "authenticated": authenticated,
        "command_available": has_command,
    }
# ============================================================
# CLEAR CURRENT COMMAND
# ============================================================
@app.delete("/kart/command/{kart_id}")
def clear_command(
    kart_id: str,
):
    """
    Clear the currently stored dashboard command.
    """

    kart_id = kart_id.strip()

    _require_authentication(
        kart_id
    )
    with state_lock:
        kart_commands.pop(
            kart_id,
            None,
        )
    return {
        "success": True,
        "kart_id": kart_id,
        "message": "Command cleared.",
    }
# ============================================================
# LOGOUT
# ============================================================
@app.post("/kart/logout/{kart_id}")
def logout(
    kart_id: str,
):
    """
    Logout the kart and clear its active dashboard command.
    """
    kart_id = kart_id.strip()
    with state_lock:
        authenticated_karts.discard(
            kart_id
        )
        kart_commands.pop(
            kart_id,
            None,
        )
    return {
        "success": True,
        "kart_id": kart_id,
        "message": "Kart logged out.",
    }
    






