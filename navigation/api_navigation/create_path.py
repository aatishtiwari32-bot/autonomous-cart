# ============================================================
# GOOGLE ROUTES API
# ============================================================
#
# This module:
#
#     origin + destination
#             ↓
#       Google Routes API
#             ↓
#        route response
#
# The returned response is later decoded by:
#
#     decode_route.py
#
# IMPORTANT:
# API keys are NEVER hardcoded here.
#
# Supported environment variables:
#
#     GOOGLE_MAPS_API_KEY
#
# or
#
#     GMAPS_API_KEY
#
# ============================================================


import os

import requests


# ============================================================
# CONFIGURATION
# ============================================================

ROUTES_API_URL = (
    "https://routes.googleapis.com/"
    "directions/v2:computeRoutes"
)


# Request timeout in seconds.
# We do not want the robot/backend to wait forever for
# Google's server.
REQUEST_TIMEOUT = 8.0


# ------------------------------------------------------------
# API KEY
# ------------------------------------------------------------
#
# Prefer the new clear name:
#
#     GOOGLE_MAPS_API_KEY
#
# Also support the name used in your friend's repo:
#
#     GMAPS_API_KEY
#
# No hardcoded fallback key.
# ------------------------------------------------------------

API_KEY = (
    os.getenv("GOOGLE_MAPS_API_KEY")
    or os.getenv("GMAPS_API_KEY")
    or ""
)


# ============================================================
# COORDINATE CONVERSION
# ============================================================

def _get_latitude_longitude(coordinates):
    """
    Extract latitude and longitude from supported coordinate
    formats.

    Supported:

    1. Pydantic/object:
        coordinates.latitude
        coordinates.longitude

    2. Dict:
        {
            "latitude": ...,
            "longitude": ...
        }

    3. Dict:
        {
            "lat": ...,
            "lng": ...
        }

    4. Dict:
        {
            "lats": ...,
            "longs": ...
        }

    5. Tuple/list:
        (latitude, longitude)

    Returns:
        (latitude, longitude)

    Raises:
        ValueError if coordinates are invalid.
    """

    if coordinates is None:
        raise ValueError(
            "Coordinates cannot be None"
        )

    # --------------------------------------------------------
    # Tuple / List
    # --------------------------------------------------------

    if isinstance(
        coordinates,
        (tuple, list)
    ):

        if len(coordinates) < 2:
            raise ValueError(
                "Coordinate sequence must contain "
                "latitude and longitude"
            )

        return (
            float(coordinates[0]),
            float(coordinates[1])
        )

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(
        coordinates,
        dict
    ):

        if (
            "latitude" in coordinates
            and
            "longitude" in coordinates
        ):

            return (
                float(
                    coordinates["latitude"]
                ),
                float(
                    coordinates["longitude"]
                )
            )

        if (
            "lat" in coordinates
            and
            "lng" in coordinates
        ):

            return (
                float(
                    coordinates["lat"]
                ),
                float(
                    coordinates["lng"]
                )
            )

        if (
            "lats" in coordinates
            and
            "longs" in coordinates
        ):

            return (
                float(
                    coordinates["lats"]
                ),
                float(
                    coordinates["longs"]
                )
            )

        raise ValueError(
            "Dictionary must contain one of: "
            "(latitude, longitude), "
            "(lat, lng), "
            "(lats, longs)"
        )

    # --------------------------------------------------------
    # Object / Pydantic model
    # --------------------------------------------------------

    if (
        hasattr(coordinates, "latitude")
        and
        hasattr(coordinates, "longitude")
    ):

        return (
            float(
                coordinates.latitude
            ),
            float(
                coordinates.longitude
            )
        )

    raise ValueError(
        f"Unsupported coordinate type: "
        f"{type(coordinates).__name__}"
    )


# ============================================================
# GOOGLE LOCATION FORMAT
# ============================================================

def coordinates_to_location(
    coordinates
):
    """
    Convert project coordinates to the Google Routes API
    location format.
    """

    latitude, longitude = (
        _get_latitude_longitude(
            coordinates
        )
    )

    return {
        "location": {
            "latLng": {
                "latitude": latitude,
                "longitude": longitude
            }
        }
    }


# ============================================================
# API KEY CHECK
# ============================================================

def _has_api_key():
    """
    Check whether a Google Maps API key is configured.
    """

    return bool(
        API_KEY
        and
        API_KEY.strip()
    )


# ============================================================
# REQUEST BODY
# ============================================================

def _build_route_request(
    origin,
    destination
):
    """
    Build the ComputeRoutes request body.
    """

    return {
        "origin": coordinates_to_location(
            origin
        ),

        "destination": coordinates_to_location(
            destination
        ),

        "travelMode": "DRIVE",

        # We only need the primary route.
        "computeAlternativeRoutes": False,

        # Metric distance values are useful for the robot.
        "units": "METRIC",
    }


# ============================================================
# REQUEST HEADERS
# ============================================================

def _build_headers():
    """
    Build HTTP headers for Google Routes API.
    """

    return {
        "Content-Type": "application/json",

        "X-Goog-Api-Key": API_KEY,

        # Only request fields actually consumed by our
        # navigation system.
        #
        # This keeps the API response smaller and avoids
        # unnecessary response computation.
        "X-Goog-FieldMask": (
            "routes.distanceMeters,"
            "routes.duration,"
            "routes.polyline.encodedPolyline"
        ),
    }


# ============================================================
# GOOGLE ROUTE
# ============================================================

def get_google_route(
    origin,
    destination
):
    """
    Get a route from Google Routes API.

    Parameters
    ----------
    origin:
        Start coordinates.

    destination:
        End coordinates.

    Returns
    -------
    dict or None

    Successful example:

        {
            "routes": [
                {
                    "distanceMeters": 1234,
                    "duration": "123s",
                    "polyline": {
                        "encodedPolyline": "..."
                    }
                }
            ]
        }

    Returns None when the route cannot be obtained.
    """

    # ========================================================
    # API KEY
    # ========================================================

    if not _has_api_key():

        print(
            "Google Routes API key is not configured."
        )

        print(
            "Set GOOGLE_MAPS_API_KEY or GMAPS_API_KEY."
        )

        return None


    # ========================================================
    # BUILD REQUEST
    # ========================================================

    try:

        request_body = (
            _build_route_request(
                origin,
                destination
            )
        )

    except (
        TypeError,
        ValueError
    ) as error:

        print(
            f"Google route coordinate error: "
            f"{error}"
        )

        return None


    # ========================================================
    # BUILD HEADERS
    # ========================================================

    headers = _build_headers()


    # ========================================================
    # HTTP REQUEST
    # ========================================================

    try:

        response = requests.post(
            ROUTES_API_URL,
            headers=headers,
            json=request_body,
            timeout=REQUEST_TIMEOUT
        )

    except requests.exceptions.Timeout:

        print(
            "Google Routes API request timed out."
        )

        return None

    except requests.exceptions.ConnectionError:

        print(
            "Could not connect to Google Routes API."
        )

        return None

    except requests.exceptions.RequestException as error:

        print(
            f"Google Routes API request error: "
            f"{error}"
        )

        return None


    # ========================================================
    # STATUS CODE
    # ========================================================

    print(
        "Google Status:",
        response.status_code
    )


    if response.status_code != 200:

        print(
            "Google Routes API error:"
        )

        # Don't assume the body is valid JSON.
        try:
            print(
                response.text
            )

        except Exception:
            pass

        return None


    # ========================================================
    # JSON RESPONSE
    # ========================================================

    try:

        route_response = (
            response.json()
        )

    except ValueError:

        print(
            "Google returned an invalid JSON response."
        )

        return None


    # ========================================================
    # BASIC RESPONSE VALIDATION
    # ========================================================

    if not isinstance(
        route_response,
        dict
    ):

        print(
            "Google response is not a valid JSON object."
        )

        return None


    routes = route_response.get(
        "routes"
    )


    if not isinstance(
        routes,
        list
    ):

        print(
            "Google response does not contain a valid routes list."
        )

        return None


    if len(routes) == 0:

        print(
            "Google returned no routes."
        )

        return None


    # ========================================================
    # CHECK POLYLINE
    # ========================================================
    #
    # Our decode_route.py requires:
    #
    # routes[0]
    #     └── polyline
    #           └── encodedPolyline
    #
    # ========================================================

    first_route = routes[0]

    if not isinstance(
        first_route,
        dict
    ):

        print(
            "Google returned an invalid route object."
        )

        return None


    polyline = first_route.get(
        "polyline"
    )


    if not isinstance(
        polyline,
        dict
    ):
        print(
            "Google route does not contain a polyline."
        )
        return None
    encoded_polyline = polyline.get(
        "encodedPolyline"
    )
    if not encoded_polyline:
        print(
            "Google route contains an empty polyline."
        )
        return None
    # ========================================================
    # SUCCESS
    # ========================================================
    return route_response