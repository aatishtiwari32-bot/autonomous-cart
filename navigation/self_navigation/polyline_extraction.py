from .polyline import get_route_polyline


# ============================================================
# ROUTE RESULT → GPS POLYLINE
# ============================================================

def extract_polyline(route_result):
    """
    Convert a shortest-path result into a GPS waypoint list.

    Supported input formats
    ------------------------

    1. Result returned by short_distance():

        {
            ("A", "A1", "A2", "A6"): 280.5
        }

    2. A direct graph path:

        ("A", "A1", "A2", "A6")

    3. A list of vertices:

        ["A", "A1", "A2", "A6"]


    Returns
    -------

    list of dictionaries:

        [
            {
                "point": 1,
                "latitude": 24.436623,
                "longitude": 77.158963
            },
            ...
        ]

    Returns an empty list when the input does not contain
    a valid graph path.
    """

    # ========================================================
    # EMPTY INPUT
    # ========================================================

    if route_result is None:
        return []


    # ========================================================
    # CASE 1:
    # RESULT DICTIONARY
    # ========================================================
    #
    # Expected:
    #
    # {
    #     ("A", "A1", "A2"): 250.4
    # }
    #
    # If multiple paths are supplied, select the path having
    # the smallest total distance.
    # ========================================================

    if isinstance(route_result, dict):

        if not route_result:
            return []

        valid_results = {}

        for path, distance in route_result.items():

            # Path should be tuple/list of vertex names.
            if not isinstance(
                path,
                (tuple, list)
            ):
                continue

            # Need at least one vertex.
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

            valid_results[
                tuple(path)
            ] = numeric_distance

        if not valid_results:
            return []

        # Pick the shortest route.
        shortest_path = min(
            valid_results,
            key=valid_results.get
        )
        return get_route_polyline(
            shortest_path
        )
    # ========================================================
    # CASE 2:
    #DIRECT TUPLE / LIST PATH
    # ========================================================

    if isinstance(
        route_result,
        (tuple, list)
    ):

        if not route_result:
            return []

        # Convert to tuple to keep the route immutable while
        # it is passed through the polyline layer.
        path = tuple(
            route_result
        )

        return get_route_polyline(
            path
        )
    # ========================================================
    # UNSUPPORTED INPUT
    # ========================================================
    return []
# ============================================================
# SHORTEST ROUTE → POLYLINE ALIAS
# ============================================================
def route_to_polyline(route_result):
    """
    Alias for extract_polyline().
    Useful for code where the function name should describe
    the conversion more explicitly.
    """
    return extract_polyline(
        route_result
    )



        


