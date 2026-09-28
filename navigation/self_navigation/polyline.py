# ============================================================
# CAMPUS POLYLINE DATABASE
# ============================================================
#
# polyline_database:
#     Stores intermediate GPS points for every graph edge.
#
# Example:
#
#     "A-A1" -> A -> intermediate points -> A1
#
# These points represent the physical road geometry.
#
# polypoints_db:
#     Stores the main graph vertices.
# ============================================================


polyline_database = {

    # --------------------------------------------------------
    # B1 -> A
    # --------------------------------------------------------

    "B1-A": {
        "A": {
            "lats": 24.436623,
            "longs": 77.158963
        }
    },


    # --------------------------------------------------------
    # A -> A1
    # --------------------------------------------------------

    "A-A1": {
        "A": {
            "lats": 24.436623,
            "longs": 77.158963
        },

        "1": {
            "lats": 24.436687,
            "longs": 77.1590670
        },

        "2": {
            "lats": 24.436879,
            "longs": 77.159426
        },

        "3": {
            "lats": 24.436895,
            "longs": 77.159821
        },

        "4": {
            "lats": 24.436761,
            "longs": 77.160196
        },

        "A1": {
            "lats": 24.436647,
            "longs": 77.160325
        }
    },


    # --------------------------------------------------------
    # A1 -> A2
    # --------------------------------------------------------

    "A1-A2": {
        "A1": {
            "lats": 24.436647,
            "longs": 77.160325
        },

        "A2": {
            "lats": 24.436310,
            "longs": 77.160758
        }
    },


    # --------------------------------------------------------
    # A2 -> A6
    # --------------------------------------------------------

    "A2-A6": {
        "A2": {
            "lats": 24.436310,
            "longs": 77.160758
        },

        "A6": {
            "lats": 24.435511,
            "longs": 77.161737
        }
    },


    # --------------------------------------------------------
    # A6 -> Z
    # --------------------------------------------------------

    "A6-Z": {
        "A6": {
            "lats": 24.435511,
            "longs": 77.161737
        },

        "1": {
            "lats": 24.435816,
            "longs": 77.16144
        },

        "Z": {
            "lats": 24.436114,
            "longs": 77.162463
        }
    },


    # --------------------------------------------------------
    # Z -> Y
    # --------------------------------------------------------

    "Z-Y": {
        "Z": {
            "lats": 24.436114,
            "longs": 77.162463
        },

        "Y": {
            "lats": 24.435937,
            "longs": 77.162695
        }
    },


    # --------------------------------------------------------
    # Y -> X
    # --------------------------------------------------------

    "Y-X": {
        "Y": {
            "lats": 24.435937,
            "longs": 77.162695
        },

        "1": {
            "lats": 24.435610,
            "longs": 77.162401
        },

        "2": {
            "lats": 24.435455,
            "longs": 77.162249
        },

        "3": {
            "lats": 24.435355,
            "longs": 77.162222
        },

        "X": {
            "lats": 24.435225,
            "longs": 77.162095
        }
    },


    # --------------------------------------------------------
    # A6 -> X
    # --------------------------------------------------------

    "A6-X": {
        "A6": {
            "lats": 24.435511,
            "longs": 77.161737
        },

        "X": {
            "lats": 24.435225,
            "longs": 77.162095
        }
    },


    # --------------------------------------------------------
    # X -> W
    # --------------------------------------------------------

    "X-W": {
        "X": {
            "lats": 24.435225,
            "longs": 77.162095
        },

        "W": {
            "lats": 24.434911,
            "longs": 77.162482
        }
    },


    # --------------------------------------------------------
    # W -> A7
    # --------------------------------------------------------

    "W-A7": {
        "W": {
            "lats": 24.434911,
            "longs": 77.162482
        },

        "A7": {
            "lats": 24.434434,
            "longs": 77.162937
        }
    },


    # --------------------------------------------------------
    # A7 -> U
    # --------------------------------------------------------

    "A7-U": {
        "A7": {
            "lats": 24.434434,
            "longs": 77.162937
        },

        "U": {
            "lats": 24.434170,
            "longs": 77.163025
        }
    },


    # --------------------------------------------------------
    # U -> V
    # --------------------------------------------------------

    "U-V": {
        "U": {
            "lats": 24.434170,
            "longs": 77.163025
        },

        "V": {
            "lats": 24.434250,
            "longs": 77.163810
        }
    },


    # --------------------------------------------------------
    # B -> A
    # --------------------------------------------------------

    "B-A": {
        "B": {
            "lats": 24.436623,
            "longs": 77.158963
        },

        "A": {
            "lats": 24.436623,
            "longs": 77.158963
        }
    },


    # --------------------------------------------------------
    # B -> D
    # --------------------------------------------------------

    "B-D": {
        "B": {
            "lats": 24.436623,
            "longs": 77.158963
        },

        "1": {
            "lats": 24.435866,
            "longs": 77.158935
        },

        "2": {
            "lats": 24.435471,
            "longs": 77.158951
        },

        "3": {
            "lats": 24.434939,
            "longs": 77.158622
        },

        "4": {
            "lats": 24.434760,
            "longs": 77.158276
        },

        "D": {
            "lats": 24.434525,
            "longs": 77.158183
        }
    },


    # --------------------------------------------------------
    # D -> F
    # --------------------------------------------------------

    "D-F": {
        "D": {
            "lats": 24.434525,
            "longs": 77.158183
        },

        "1": {
            "lats": 24.434295,
            "longs": 77.158111
        },

        "2": {
            "lats": 24.433974,
            "longs": 77.158124
        },

        "3": {
            "lats": 24.433697,
            "longs": 77.158287
        },

        "4": {
            "lats": 24.433544,
            "longs": 77.158405
        },

        "F": {
            "lats": 24.433122,
            "longs": 77.158405
        }
    },


    # --------------------------------------------------------
    # F -> G
    # --------------------------------------------------------

    "F-G": {
        "F": {
            "lats": 24.433122,
            "longs": 77.158405
        },

        "G": {
            "lats": 24.432633,
            "longs": 77.159899
        }
    },


    # --------------------------------------------------------
    # G -> H
    # --------------------------------------------------------

    "G-H": {
        "G": {
            "lats": 24.432633,
            "longs": 77.159899
        },

        "H": {
            "lats": 24.432350,
            "longs": 77.160498
        }
    },


    # --------------------------------------------------------
    # H -> I
    # --------------------------------------------------------

    "H-I": {
        "H": {
            "lats": 24.432350,
            "longs": 77.160498
        },

        "I": {
            "lats": 24.432143,
            "longs": 77.161121
        }
    },


    # --------------------------------------------------------
    # I -> J
    # --------------------------------------------------------

    "I-J": {
        "I": {
            "lats": 24.432143,
            "longs": 77.161121
        },

        "J": {
            "lats": 24.432049,
            "longs": 77.161708
        }
    }
}


# ============================================================
# GRAPH VERTEX DATABASE
# ============================================================

polypoints_db = {

    "A": {
        "lats": 24.436623,
        "longs": 77.158963
    },

    "A1": {
        "lats": 24.436647,
        "longs": 77.160325
    },

    "A2": {
        "lats": 24.436310,
        "longs": 77.160758
    },

    "A6": {
        "lats": 24.435511,
        "longs": 77.161737
    },

    "Z": {
        "lats": 24.436114,
        "longs": 77.162463
    },

    "Y": {
        "lats": 24.435937,
        "longs": 77.162695
    },

    "X": {
        "lats": 24.435225,
        "longs": 77.162095
    },

    "W": {
        "lats": 24.434911,
        "longs": 77.162482
    },

    "A7": {
        "lats": 24.434434,
        "longs": 77.162937
    },

    "U": {
        "lats": 24.434170,
        "longs": 77.163025
    },

    "V": {
        "lats": 24.434250,
        "longs": 77.163810
    },

    "B": {
        "lats": 24.436623,
        "longs": 77.158963
    },

    "D": {
        "lats": 24.434525,
        "longs": 77.158183
    },

    "F": {
        "lats": 24.433122,
        "longs": 77.158405
    },

    "G": {
        "lats": 24.432633,
        "longs": 77.159899
    },

    "H": {
        "lats": 24.432350,
        "longs": 77.160498
    },

    "I": {
        "lats": 24.432143,
        "longs": 77.161121
    },

    "J": {
        "lats": 24.432049,
        "longs": 77.161708
    }
}


# ============================================================
# EDGE KEY HELPER
# ============================================================

def _edge_key(start_vertex, end_vertex):
    """
    Build the database key for an edge.

    Example:
        A, A1
        ->
        "A-A1"
    """

    return f"{start_vertex}-{end_vertex}"


# ============================================================
# SINGLE EDGE POLYLINE
# ============================================================

def get_edge_polyline(
    start_vertex,
    end_vertex
):
    """
    Return the GPS polyline for one graph edge.

    The function supports both directions.

    Example:

        get_edge_polyline("A", "A1")

    searches:

        "A-A1"

    If that does not exist, it searches:

        "A1-A"

    In the reverse case, the returned points are reversed
    so that they always travel:

        start_vertex -> end_vertex

    Returns:
        list[dict]

    Example:
        [
            {
                "point": 1,
                "latitude": 24.436623,
                "longitude": 77.158963
            },
            ...
        ]

    Returns [] if the edge is unavailable.
    """

    if (
        not start_vertex
        or not end_vertex
    ):
        return []

    # --------------------------------------------------------
    # Same vertex
    # --------------------------------------------------------

    if start_vertex == end_vertex:

        vertex = polypoints_db.get(
            start_vertex
        )

        if vertex is None:
            return []

        return [
            {
                "point": 1,
                "latitude": float(
                    vertex["lats"]
                ),
                "longitude": float(
                    vertex["longs"]
                )
            }
        ]

    # --------------------------------------------------------
    # Forward edge
    # --------------------------------------------------------

    forward_key = _edge_key(
        start_vertex,
        end_vertex
    )

    if forward_key in polyline_database:

        raw_points = polyline_database[
            forward_key
        ]

        return _format_polyline_points(
            raw_points
        )

    # --------------------------------------------------------
    # Reverse edge
    # --------------------------------------------------------

    reverse_key = _edge_key(
        end_vertex,
        start_vertex
    )

    if reverse_key in polyline_database:

        raw_points = polyline_database[
            reverse_key
        ]

        return _format_polyline_points(
            raw_points,
            reverse=True
        )

    return []


# ============================================================
# FORMAT RAW POLYLINE
# ============================================================

def _format_polyline_points(
    raw_points,
    reverse=False
):
    """
    Convert raw database points into the common waypoint
    format expected by navigation.py.

    Parameters
    ----------
    raw_points:
        Dictionary of polyline coordinates.

    reverse:
        Whether the route is being traversed backward.
    """

    if not raw_points:
        return []

    values = list(
        raw_points.values()
    )

    if reverse:
        values.reverse()

    result = []

    for point in values:

        try:

            result.append({
                "point": len(result) + 1,
                "latitude": float(
                    point["lats"]
                ),
                "longitude": float(
                    point["longs"]
                )
            })

        except (
            KeyError,
            TypeError,
            ValueError
        ):
            # Ignore malformed point
            continue

    return result


# ============================================================
# COMPLETE ROUTE POLYLINE
# ============================================================

def get_route_polyline(path):
    """
    Convert a graph path into a continuous GPS waypoint list.

    Example:

        path = (
            "A",
            "A1",
            "A2",
            "A6"
        )

    becomes:

        A
        ↓
        intermediate points
        ↓
        A1
        ↓
        A2
        ↓
        A6

    Duplicate connecting points are removed.

    Returns:
        list[dict]
    """

    if not path:
        return []

    # Accept list / tuple
    path = list(path)

    # --------------------------------------------------------
    # Single vertex
    # --------------------------------------------------------

    if len(path) == 1:

        vertex = polypoints_db.get(
            path[0]
        )

        if vertex is None:
            return []

        return [
            {
                "point": 1,
                "latitude": float(
                    vertex["lats"]
                ),
                "longitude": float(
                    vertex["longs"]
                )
            }
        ]

    final_points = []

    # ========================================================
    # Stitch every consecutive edge
    # ========================================================

    for index in range(
        len(path) - 1
    ):

        start_vertex = path[index]
        end_vertex = path[index + 1]

        edge_points = get_edge_polyline(
            start_vertex,
            end_vertex
        )

        if not edge_points:
            continue

        # ----------------------------------------------------
        # Avoid duplicate connecting point
        # ----------------------------------------------------

        if final_points:

            previous = final_points[-1]
            first = edge_points[0]

            same_point = (
                abs(
                    previous["latitude"]
                    - first["latitude"]
                ) < 1e-9
                and
                abs(
                    previous["longitude"]
                    - first["longitude"]
                ) < 1e-9
            )

            if same_point:
                edge_points = edge_points[1:]

        final_points.extend(
            edge_points
        )

    # --------------------------------------------------------
    # Re-number final points
    # --------------------------------------------------------

    for index, point in enumerate(
        final_points,
        start=1
    ):
        point["point"] = index

    return final_points


# ============================================================
# VERTEX COORDINATE HELPER
# ============================================================

def get_vertex_coordinates(
    vertex
):
    """
    Return coordinates of a graph vertex.

    Output:

        {
            "latitude": ...,
            "longitude": ...
        }

    Returns None if vertex does not exist.
    """

    data = polypoints_db.get(
        vertex
    )

    if data is None:
        return None

    return {
        "latitude": float(
            data["lats"]
        ),
        "longitude": float(
            data["longs"]
        )
    }


# ============================================================
# DATABASE VALIDATION
# ============================================================

def validate_polyline_database():
    """
    Validate that every polyline edge contains usable
    latitude/longitude data.

    Returns:

        {
            "valid": True,
            "errors": []
        }

    or:

        {
            "valid": False,
            "errors": [...]
        }
    """

    errors = []

    for edge_name, raw_points in (
        polyline_database.items()
    ):

        # ----------------------------------------------------
        # Edge name
        # ----------------------------------------------------

        if "-" not in edge_name:

            errors.append(
                f"Invalid edge name: {edge_name}"
            )

            continue

        # ----------------------------------------------------
        # Points
        # ----------------------------------------------------

        if not isinstance(
            raw_points,
            dict
        ):

            errors.append(
                f"{edge_name}: points must be a dictionary"
            )

            continue

        for point_name, point in (
            raw_points.items()
        ):

            if not isinstance(
                point,
                dict
            ):

                errors.append(
                    f"{edge_name}/{point_name}: "
                    "invalid point"
                )

                continue

            if (
                "lats" not in point
                or
                "longs" not in point
            ):

                errors.append(
                    f"{edge_name}/{point_name}: "
                    "missing lats/longs"
                )
                continue
            try:
                float(point["lats"])
                float(point["longs"])
            except (
                TypeError,
                ValueError
            ):
                errors.append(
                    f"{edge_name}/{point_name}: "
                    "coordinates are not numeric"
                )
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }