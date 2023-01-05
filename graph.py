from math import sqrt, inf
from geometry import in_polygon, intersect

INF = inf


def add_edge(graph, map, u, v, u_coords, v_coords):
    xi, yi = u_coords
    xj, yj = v_coords

    if not in_polygon(map, (xi + xj) / 2, (yi + yj) / 2):
        return graph

    is_intersect = False

    for p1 in range(len(map) - 1):
        p2 = (p1 + 1) % (len(map) - 1)
        if p1 == u or p1 == v or p2 == u or p2 == v:
            continue
        if intersect(u_coords, v_coords, map[p1], map[p2]):
            is_intersect = True
            break

    if is_intersect:
        return graph

    dx, dy = xj - xi, yj - yi
    w = sqrt(dx * dx + dy * dy)

    if u not in graph:
        graph[u] = {}

    graph[u][v] = w

    if v not in graph:
        graph[v] = {}

    graph[v][u] = w

    return graph


def generate_graph(map):
    graph = {}

    for u in range(len(map) - 1):
        v = (u + 1) % (len(map) - 1)
        u_coords = map[u]
        v_coords = map[v]

        xu, yu = u_coords
        xv, yv = v_coords

        dx, dy = xv - xu, yv - yu
        w = sqrt(dx * dx + dy * dy)

        if u not in graph:
            graph[u] = {}

        if v not in graph:
            graph[v] = {}

        graph[u][v] = graph[v][u] = w

        for i in range(u + 2, len(map) - 1):
            graph = add_edge(graph, map, u, i, map[u], map[i])
    return graph


def pq_pop(pq):
    res = []
    res_i = -1
    res_u = -1
    res_w = inf
    for i, (u, w) in enumerate(pq):
        res.append((u, w))
        if w < res_w:
            res_i = i
            res_u = u
            res_w = w
    del res[res_i]
    return res, (res_u, res_w)


def pathfind(graph, map, start_coords, end_coords):
    if not start_coords or not end_coords:
        return

    n = len(map) - 1

    for u in range(n):
        coords = map[u]
        graph = add_edge(graph, map, -1, u, start_coords, coords)
        graph = add_edge(graph, map, -2, u, end_coords, coords)
    graph = add_edge(graph, map, -1, -2, start_coords, end_coords)

    dist = {i: inf for i in range(-2, len(graph) - 2)}
    dist[-1] = 0
    pq = [(-1, 0)]
    prev = {i: -3 for i in range(-2, len(graph) - 2)}

    while len(pq):
        pq, (u, coords) = pq_pop(pq)

        for v in graph[u]:
            if dist[v] > dist[u] + graph[u][v]:
                dist[v] = dist[u] + graph[u][v]
                prev[v] = u
                pq.append((v, dist[v]))

    path = [end_coords]
    trace = prev[-2]

    while trace != -1:
        path.append(map[trace])
        trace = prev[trace]

    path.append(start_coords)

    return path, dist[-2]


def remove_start_end(graph):
    if -1 in graph:
        del graph[-1]
    if -2 in graph:
        del graph[-2]
    for u in graph:
        if -1 in graph[u]:
            del graph[u][-1]
        if -2 in graph[u]:
            del graph[u][-2]

    return graph
