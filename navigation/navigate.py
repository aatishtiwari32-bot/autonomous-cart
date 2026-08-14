import math
from fnpp import polypoint
def calculate_bearing(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2
    # Degrees -> radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    # Geographic bearing components
    y = math.sin(delta_lon) * math.cos(lat2)
    x = (
        math.cos(lat1) * math.sin(lat2)
        -
        math.sin(lat1)
        * math.cos(lat2)
        * math.cos(delta_lon)
    )
    # Angle from North
    bearing = math.atan2(y, x)
    # Radians -> degrees
    bearing = math.degrees(bearing)
    # Keep bearing between 0 and 360
    bearing = (bearing + 360) % 360
    return bearing
def angle_difference(desired_bearing, current_bearing):
    difference = desired_bearing - current_bearing
    # Normalize between -180 and +180
    difference = (difference + 180) % 360 - 180
    return difference
def generate_command(angle_error):
    if abs(angle_error) <= 10:
        return "F"
    elif 10 < angle_error <= 30:
        return "SR"
    elif -30 <= angle_error < -10:
        return "SL"
    elif angle_error > 30:
        return "R"
    else:
        return "L"
def navigate(heading , current_coords, points):
    next_point = polypoint(
        current_coords,
        points
    )
    desired_bearing = calculate_bearing(
        current_coords,
        next_point
    )
    angle_error = angle_difference(
        desired_bearing,
        heading
    )
    command = generate_command(angle_error)
    return {
        "command": command
    }