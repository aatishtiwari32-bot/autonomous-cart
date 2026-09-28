# ============================================================
# GRAPH PATH -> VERTEX WAYPOINTS
# ============================================================

from .polyline import polypoints_db


# ============================================================
# PATH EXTRACTION
# ============================================================

def _extract_path(route_result):
    """
    Extract a graph path tuple from supported route formats.

    Supported:

    1. Direct tuple:
        ("A", "A1", "A2", "A6")

    2. Direct list:
        ["A", "A1", "A2", "A6"]

    3. Shortest-distance result:
        {
            ("A", "A1", "A2"): 250.5
        }

    When a dictionary contains multiple paths, the path
    having the smallest numeric distance is selected.

    Returns:
        tuple
        or
        None
    """

    if route_result is None:
        return None

    # --------------------------------------------------------
    # Dictionary result
    # --------------------------------------------------------

    if isinstance(route_result, dict):

        if not route_result:
            return None

        valid_paths = {}

        for path, distance in route_result.items():

            if not isinstance(
                path,
                (tuple, list)
            ):
                continue

            if len(path) == 0:
                continue

            try:
                numeric_distance = float(
                    distance
                )
            except (
                TypeError,
                ValueError
            ):
                continue

            valid_paths[
                tuple(path)
            ] = numeric_distance

        if not valid_paths:
            return None

        shortest_path = min(
            valid_paths,
            key=valid_paths.get
        )

        return shortest_path

    # --------------------------------------------------------
    # Tuple / list
    # --------------------------------------------------------

    if isinstance(
        route_result,
        (tuple, list)
    ):

        if not route_result:
            return None

        return tuple(
            route_result
        )

    return None


# ============================================================
# MAIN CONVERTER
# ============================================================

def result_convertor(route_result):
    """
    Convert graph vertices into their corresponding GPS
    coordinates.

    Example input:

        (
            "A",
            "A1",
            "A2"
        )

    Example output:

        [
            {
                "point": 1,
                "latitude": 24.436623,
                "longitude": 77.158963
            },
            {
                "point": 2,
                "latitude": 24.436647,
                "longitude": 77.160325
            },
            {
                "point": 3,
                "latitude": 24.436310,
                "longitude": 77.160758
            }
        ]
    NOTE:
    This function converts GRAPH VERTICES only.
    It does NOT add intermediate road/polyline points.
    For the complete dense road route, use:
        extract_polyline()
        or
        get_route_polyline()
    """
    path = _extract_path(
        route_result
    )
    if path is None:
        return []
    points = []
    for vertex in path:
        # ----------------------------------------------------
        # Vertex must exist in coordinate database
        # ----------------------------------------------------
        vertex_data = polypoints_db.get(
            vertex
        )
        if vertex_data is None:
            # If one graph vertex has no coordinate data,
            # the route cannot be represented correctly.
            return []
        try:
            latitude = float(
                vertex_data["lats"]
            )
            longitude = float(
                vertex_data["longs"]
            )
        except (
            KeyError,
            TypeError,
            ValueError
        ):
            return []
        points.append({
            "point": len(points) + 1,
            "latitude": latitude,
            "longitude": longitude
        })
    return points
# ============================================================
# EXPLICIT ALIAS
# ============================================================
def convert_path_to_points(route_result):
    """
    Explicit alias for result_convertor().

    Useful when readability is preferred over the older
    function name.
    """

    return result_convertor(
        route_result
    )
