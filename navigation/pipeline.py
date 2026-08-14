from create_path import get_google_route
from decode_route import extract_route_points
from navigate import navigate
from movement import movement
def pipeline(mp, k, dp, He, frame):
    receive_path = get_google_route(k, mp)
    deliver_path = get_google_route(k, dp)
    receive_points = extract_route_points(receive_path)
    deliver_points = extract_route_points(deliver_path)
    global current_route
    current_route = 1
    if current_route == 1:
        map_command = navigate(He, k, receive_points)
    if mp == k:
        current_route = 2
        map_command = navigate(He, k, deliver_points)
    basic_cmd = movement(frame)
    if basic_cmd == "STOP":
        return "STOP"
    elif basic_cmd == "MOVE":
        return map_command.get("command")
    return "STOP"

