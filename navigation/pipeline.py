from api_navigation.create_path import get_google_route
from api_navigation.decode_route import extract_route_points
from navigation_tools.navigate import navigate
from navigation_tools.movement import movement
from other_tools.frame_extraction import get_frame
from navigation_tools.close_coords import close_coords as csd
from navigation_tools.close_coords import very_close_coords as vcc
from self_navigation.distance_graph import juet_weighted_graph
from self_navigation.shortest_distance import short_distance
from self_navigation.polyline_extraction import extract_polyline
def pipeline(mp, k, dp, He, sd):
    frame = get_frame()
    basic_cmd = movement(frame)
    ''' SELF DEPENDENCE AGAR 1 HAI TOH APNI ROUTING LAGAAYI '''
    current_route = 1
    if(vcc(k, mp)):
        current_route = 2
    if(sd == 1):
        ''' ese case mei hum receive points aur deliver points nikaalenge aur p'''
        receive_distance_list  = short_distance(k, mp)
        deliver_distance_list = short_distance(k, dp)
        receive_points = extract_polyline(receive_distance_list)
        deliver_points = extract_polyline(deliver_distance_list)
        if(current_route == 1):
            map_command = navigate(He, k, receive_points)
        else:
            map_command = navigate(He, k, dp, deliver_points)
    elif(sd == 0):
        receive_path = get_google_route(k, mp)
        deliver_path = get_google_route(k, dp)
        receive_points = extract_route_points(receive_path)
        deliver_points = extract_route_points(deliver_path)
        if(current_route == 1):
            map_command = navigate(He, k, receive_points)
        else:
            map_command = navigate(He, k, dp, deliver_points)
    if basic_cmd["obstacle_present"] == "true":
        return basic_cmd.get("command","stop")
    elif basic_cmd["obstacle_present"] == "false":
        return map_command.get("command")
    return "STOP"
    ''' yaha par puraana api vaala scene karenge hum '''
    

