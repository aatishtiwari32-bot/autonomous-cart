from polyline import polypoints_db
def result_convertor(init_result):
    points = []
    vertex_size = len(init_result.key())
    current_vertex = init_result.key()[0]
    for i in range(vertex_size):
        points.append({"point": i+1, "latitude": polypoints_db[current_vertex][lats], "longitude": polypoints_db[current_vertex][longs]})
    return points   



