import math
from knot import *
import SeifertMaker

n_edges = 100
r = 1
crossing_coords = (Point(0,0,0), Point(2,0,0), Point(1, 0, math.sqrt(3)))

#horrible code to make trefoil
bottom_circle = ((1, 0, 0), math.pi, math.pi*2, crossing_coords[0],  crossing_coords[1])
right_circle = ((3/2, 0, math.sqrt(3)/2), -math.pi/3, 2 * math.pi/3, crossing_coords[1],  crossing_coords[2])
left_circle = ((0.5, 0, math.sqrt(3)/2), math.pi/3, 4 * math.pi/3, crossing_coords[2],  crossing_coords[0])
circles_to_add = [bottom_circle, right_circle, left_circle]
circles = []
for circle in circles_to_add:
    circ_vertices = []
    theta1 = circle[1]
    theta2 = circle[2]
    dTheta = (theta2 - theta1) / n_edges
    center = circle[0]

    for i in range(0, n_edges + 1):
        theta = theta1 + i * dTheta
        vertex = (r * math.cos(theta) + center[0] , 0, r * math.sin(theta) + center[2])
        circ_vertices.append(vertex)

    new_circle = Edge(circ_vertices, circle[3], circle[4])
    circles.append(new_circle)

def create_line(point1, point2):
    dx = (point2.x-point1.x)/n_edges
    dz = (point2.z-point1.z)/n_edges
    path = []
    for i in range(n_edges + 1):
        point = (point1.x + dx * i, 0, point1.z + dz * i)
        path.append(point)
    return Edge(path, point1, point2)

left_side = create_line(crossing_coords[2], crossing_coords[0])
bottom_side = create_line(crossing_coords[0], crossing_coords[1])
right_side = create_line(crossing_coords[1], crossing_coords[2])

left_crossing = Crossing(crossing_coords[0], Strands(bottom_side, circles[0], circles[2], left_side))
right_crossing = Crossing(crossing_coords[1], Strands(right_side, circles[1], circles[0], bottom_side))
top_crossing = Crossing(crossing_coords[2], Strands(left_side, circles[2], circles[1], right_side))

trefoil = Knot([left_crossing, right_crossing, top_crossing])

SeifertMaker.createSeifertSurface(trefoil)
