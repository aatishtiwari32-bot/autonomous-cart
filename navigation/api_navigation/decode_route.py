"""
Google Routes API polyline decoder.

Converts Google's encoded polyline string into a list of
latitude/longitude points.

Output format:
[
    {
        "point": 1,
        "latitude": 24.435455,
        "longitude": 77.162249
    },
    ...
]
"""


def _decode_value(encoded: str, index: int):
    """
    Decode one latitude/longitude value from an encoded polyline.

    Returns:
        tuple[int, int]:
            (decoded_value, new_index)

        Returns (None, index) if the encoded string is invalid.
    """

    result = 0
    shift = 0

    while True:

        # Prevent reading beyond the string.
        if index >= len(encoded):
            return None, index

        byte = ord(encoded[index]) - 63
        index += 1

        # Valid polyline characters should produce non-negative values.
        if byte < 0:
            return None, index

        result |= (byte & 0x1F) << shift
        shift += 5

        # Last chunk of this value.
        if byte < 0x20:
            break

        # Safety against corrupted input causing excessive shifting.
        if shift > 60:
            return None, index

    # Convert from unsigned encoded value to signed delta.
    if result & 1:
        value = ~(result >> 1)
    else:
        value = result >> 1

    return value, index


def decode_polyline(encoded):
    """
    Decode a Google encoded polyline string.

    Args:
        encoded (str): Encoded polyline.

    Returns:
        list[dict]: Decoded GPS points.

        Returns [] for invalid input.
    """

    if not isinstance(encoded, str):
        return []

    if not encoded:
        return []

    points = []

    index = 0
    latitude = 0
    longitude = 0

    while index < len(encoded):

        # Decode latitude delta.
        delta_latitude, index = _decode_value(encoded, index)

        if delta_latitude is None:
            return []

        # Decode longitude delta.
        delta_longitude, index = _decode_value(encoded, index)

        if delta_longitude is None:
            return []

        latitude += delta_latitude
        longitude += delta_longitude

        points.append(
            {
                "point": len(points) + 1,
                "latitude": latitude / 100000.0,
                "longitude": longitude / 100000.0,
            }
        )

    return points


def extract_route_points(route_response):
    """
    Extract and decode the first route's encoded polyline.

    Expected Google Routes API response structure:

    {
        "routes": [
            {
                "polyline": {
                    "encodedPolyline": "..."
                }
            }
        ]
    }

    Args:
        route_response (dict): Google Routes API response.

    Returns:
        list[dict]: Decoded GPS points.
    """

    if not isinstance(route_response, dict):
        return []
    routes = route_response.get("routes")
    if not isinstance(routes, list) or not routes:
        return []
    route = routes[0]
    if not isinstance(route, dict):
        return []
    polyline = route.get("polyline")
    if not isinstance(polyline, dict):
        return []
    encoded = polyline.get("encodedPolyline")
    if not isinstance(encoded, str) or not encoded:
        return []
    return decode_polyline(encoded)
# Backward-compatible alias.
route_to_points = extract_route_points