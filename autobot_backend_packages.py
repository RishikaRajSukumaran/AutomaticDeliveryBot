import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
from networkx.algorithms.approximation import traveling_salesman_problem
import numpy as np
import json
import webbrowser
import time

def interpolate(start, end, interval):
    pts=[list(start)]
    dist=geodesic(start, end).meters  #distance(in m)
    if dist>interval:
        numpts=int(dist//interval)
        for i in range(1, numpts + 1):
            lat=start[0]+(end[0]-start[0])*(i*interval / dist)
            lon=start[1]+(end[1]-start[1])*(i*interval / dist)
            pts.append([lat, lon])
    pts.append(list(end))
    return pts

def bellman_ford_shortest_path(graph, source, target, weight="weight"):

    nodedistance={node: float("inf") for node in graph.nodes}
    nodepredecessor={node: None for node in graph.nodes}
    nodedistance[source]=0

    for _ in range(len(graph.nodes)-1):
        for u, v, data in graph.edges(data=True):
            edge_weight=data.get(weight, 1)  #default weight = 1 if not provided
            if nodedistance[u]+edge_weight<nodedistance[v]:
                nodedistance[v]=nodedistance[u]+edge_weight
                nodepredecessor[v]=u
            if nodedistance[v]+edge_weight<nodedistance[u]:#handles undirected edges
                nodedistance[u]=nodedistance[v]+edge_weight
                nodepredecessor[u]=v

    #check negative weight cycle
    for u, v, data in graph.edges(data=True):
        edge_weight=data.get(weight, 1)
        if nodedistance[u]+edge_weight<nodedistance[v]:
            raise ValueError("Graph contains a negative weight cycle.")

    path=[]
    current=target
    while current is not None:
        path.append(current)
        current=nodepredecessor[current]

    path.reverse()

    if path[0]!=source:  #if the source is not the start of the path
        raise ValueError(f"No path exists between {source} and {target}.")

    return path

def totdistance(coords):
    totdist=0
    for i in range(len(coords) - 1):
        totdist+=geodesic(coords[i], coords[i + 1]).meters
    return totdist

def road_small(startli:list, endli:list):
    placename="Central Park, New York, USA"
    graph=ox.graph_from_place(placename, network_type="walk")

    #start & end points
    start_point=tuple(startli)
    end_point=tuple(endli)

    #nearest nodes in the graph to the input coordinates
    start_node=ox.distance.nearest_nodes(graph, X=start_point[1], Y=start_point[0])
    end_node=ox.distance.nearest_nodes(graph, X=end_point[1], Y=end_point[0])

    #shortest path between the nodes
    shortestpath=bellman_ford_shortest_path(graph, source=start_node, target=end_node, weight="length")

    # Extract the route coordinates (latitude, longitude) for the path
    routecoords=[(graph.nodes[i]["y"], graph.nodes[i]["x"]) for i in shortestpath]

    #generate interpolated path coordinates
    pathcords = []
    for i in range(len(routecoords) - 1):
        start=routecoords[i]
        end=routecoords[i + 1]
        pathcords.extend(interpolate(start, end, 10))

    distance=totdistance(routecoords)

    output={"routeCoords": pathcords,"startCoord": startli, "endCoords": [endli]}
    time.sleep(4)
    with open("path_coordinates.json", "w") as json_file:
        json.dump(output, json_file, indent=2)

    html_url="http://localhost:8000/botmap.html"
    webbrowser.open(html_url)
    return int(distance)

def road_big(startli:list, endli:list):

    start_point=tuple(startli)
    end_points=[tuple(i) for i in endli]

    placename="Central Park, New York, USA"
    graph=ox.graph_from_place(placename, network_type="walk")

    #nearest nodes to start and end points
    start_node=ox.distance.nearest_nodes(graph, start_point[1], start_point[0])
    end_nodes=[
        ox.distance.nearest_nodes(graph, i[1], i[0])
        for i in end_points
    ]
    all_nodes =[start_node]+end_nodes

    #Create a subgraph with distances between start and end nodes
    subgraph=nx.Graph()
    for i in range(len(all_nodes)):
        for j in range(i + 1, len(all_nodes)):
            source, target=all_nodes[i], all_nodes[j]
            try:
                length=nx.shortest_path_length(graph, source=source, target=target, weight="length")
                subgraph.add_edge(source, target, weight=length)
            except nx.NetworkXNoPath:
                continue

    #using Traveling Salesman Problem
    optimal_order=traveling_salesman_problem(subgraph, cycle=False)

    #full route based on optimal order
    route_nodes=[]
    routecoords=[]

    for i in range(len(optimal_order) - 1):
        source=optimal_order[i]
        target=optimal_order[i + 1]
        path_segment=bellman_ford_shortest_path(graph, source=source, target=target, weight="length")
        route_nodes.extend(path_segment[:-1])
        segment_coords=[(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in path_segment[:-1]]
        routecoords.extend(segment_coords)

    # Add final node
    final_node=optimal_order[-1]
    route_nodes.append(final_node) #node unique id
    routecoords.append((graph.nodes[final_node]['y'], graph.nodes[final_node]['x']))

    # Interpolate coordinates along route
    pathcords=[]
    for i in range(len(routecoords) - 1):
        start=routecoords[i]
        end=routecoords[i + 1]
        pathcords.extend(interpolate(start, end, 5))
        pathcords.reverse()

    distance=totdistance(routecoords)

    output={"routeCoords": pathcords, "startCoord": startli, "endCoords": endli}
    time.sleep(4)
    with open("path_coordinates.json", "w") as json_file:
        json.dump(output, json_file, indent=2)

    html_url="http://localhost:8000/botmap.html"
    webbrowser.open(html_url)
    return int(distance)

def air_single(startli:list,endli:list):

    #start and end coordinates
    start = tuple(startli)  # eg: start: New York (latitude, longitude)
    end = tuple(endli)  # eg: end: Another point in New York

    pathcoords=interpolate(start, end, 12)
    distance=geodesic(start, end).meters

    output={"routeCoords": pathcoords, "startCoord": startli, "endCoords": [endli]}
    time.sleep(4)
    with open("path_coordinates.json", "w") as json_file:
        json.dump(output, json_file, indent=2)

    html_url="http://localhost:8000/botmap.html"
    webbrowser.open(html_url)
    return int(distance)

def air_multiple(startli: list, endli: list):

    def calculate_distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    # Define start and multiple waypoints
    start_point=tuple(startli)
    end_points=[tuple(i) for i in endli]
    points=[start_point] + end_points  #Combine start and endpoints

    #solve the TSP using a greedy approach
    def tsp_greedy(points):
        unvisited=points[:]
        current_point=unvisited.pop(0)  #start point
        route=[current_point]

        while unvisited:
            #nearest neighbor to the current point
            nearest_point=min(unvisited, key=lambda p: calculate_distance(current_point, p))
            route.append(nearest_point)
            unvisited.remove(nearest_point)
            current_point=nearest_point

        return route

    #solve TSP and get the optimal path
    best_route=tsp_greedy(points)

    #interpolate the points along the best route
    pathcoords=[]
    for i in range(len(best_route) - 1):
        pathcoords.extend(interpolate(best_route[i], best_route[i + 1], 5))

    total_geodesic_distance = totdistance(pathcoords)

    output = {"routeCoords": pathcoords, "startCoord": startli, "endCoords": endli}
    time.sleep(4)
    with open("path_coordinates.json", "w") as json_file:
        json.dump(output, json_file, indent=2)

    html_url = "http://localhost:8000/botmap.html"
    webbrowser.open(html_url)

    return int(total_geodesic_distance)
#
# startli = [40.768731, -73.981803]  # Eg:start point in Central Park
# endli = [40.771133, -73.974187]   # Eg: end point in Central Park
#
# road_small(startli, endli)
# start = [40.793535, -73.958129]
# end = [
#     [40.788044, -73.966583],
#     [40.781577, -73.967631],
#     [40.777464, -73.967080],
# ]
#
# road_big(start, end)
# endli = [40.748817, -73.985428]  # Start point
# startli = [40.758896, -73.985130]    # End point
#
# air_single(startli, endli)
#
# startli = [40.748817, -73.985428]  # Start point
# endli = [
#     [40.758896, -73.985130],  # Waypoint 1
#     [40.7614, -73.9776],      # Waypoint 2
#     [40.7527, -73.9772]       # Waypoint 3
# ]
# air_multiple(startli, endli)





