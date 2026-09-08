from distance_graph import juet_weighted_graph
from close_coords import close_coords as cc
def extract_vertices(current_vertex, end_vertex, path, distance, result):
    # Target mil gaya
    if current_vertex == end_vertex:
        result[tuple(path)] = distance
        return
    connections = juet_weighted_graph[current_vertex]["connections"]
    for next_vertex, edge_distance in connections.items():
        # Vertex already path mein hai -> repeat nahi hone dena
        if next_vertex in path:
            continue
        # Nayi path
        new_path = path + [next_vertex]
        # Naya total distance
        new_distance = distance + edge_distance
        # Aage explore karo
        extract_vertices(
            next_vertex,
            end_vertex,
            new_path,
            new_distance,
            result
        )
def short_distance(kart_coords, target_coords):
    ''' START AUR ENDING KE COORDINATES SE DONO KE RESPECTIVE VERTEX NIKAALE HAI '''
    start_vertex = cc(kart_coords)
    end_vertex = cc(target_coords)
    result = {}
    extract_vertices(
        start_vertex,
        end_vertex,
        [start_vertex],
        0,
        result
    )
    # Koi route nahi mila
    if not result:
        return {}
    # Minimum distance wala path
    shortest_path = min(
        result,
        key=result.get
    )
    final_result = result_convertor(result)

    return {
        final_result
    }
'''
output will be in from of:
{
    ("A", "A1", "A2", "A6", "X", "W", "A7", "U", "J"): 746.69
}
WANTED OUTPUT:
points = [{
            "point": len(points) + 1,
            "latitude": latitude / 100000.0,
            "longitude": longitude / 100000.0
        }]
'''