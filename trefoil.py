import math

class Edge:
    def __init__(self, vertices, origin, dest):
        self.vertices = vertices
        self.origin = origin
        self.dest = dest

    def __str__(self):
        return f"{self.origin} -> {self.dest} ({id(self)})"

    def endpoints(self):
        return (self.origin, self.dest)

class Crossing:
     def __init__(self, coord, strands):
         self.coord = coord
         self.strands = strands

class Point:
    def __init__(self, x, z):
        self.x = x
        self.z = z

    def __str__(self):
        return f"{self.x}, {self.z}"

class Strands:
    def __init__(self, oo, ou, io, iu):
         self.oo = oo
         self.ou = ou
         self.io = io
         self.iu = iu

class Knot:
    def __init__(self, crossings):
        self.crossings = crossings

n_edges = 100
r = 1
crossing_coords = (Point(0,0), Point(2,0), Point(1, math.sqrt(3)))

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

#making seifert circles

seifert_circles = []

for crossing in trefoil.crossings:
    joints = [(crossing.strands.oo, crossing.strands.iu), (crossing.strands.io, crossing.strands.ou)]
    for joint in joints:
        circlesToJoin = []
        for edge in joint:
            for circle in seifert_circles:
                if edge in circle:
                    seifert_circles.remove(circle)
                    circlesToJoin.append(circle)
                    break
        if len(circlesToJoin) == 2:
            seifert_circles.append(circlesToJoin[0].union(circlesToJoin[1]))
        elif len(circlesToJoin) == 1:
            seifert_circles.append(circlesToJoin[0].union(joint))
        else:
            seifert_circles.append(set(joint))

print(f"genus is {(len(trefoil.crossings) - len(seifert_circles) + 1)//2}")

#reorder circles for easy drawing
drawable_circles = []

for circle in seifert_circles:
    curEdge = circle.pop()
    redefinedCircle = [curEdge]
    circ_origin = curEdge.origin
    startFound = False
    while not startFound:
        for edge in circle:
            if curEdge.dest in edge.endpoints():
                if curEdge.dest != edge.origin:
                    edge.vertcies.reverse()
                    temp = edge.origin
                    edge.origin = edge.dest
                    edge.dest = temp
                redefinedCircle.append(edge)
                circle.remove(edge)
                curEdge = edge
                startFound = circ_origin in edge.endpoints()
                break
    drawable_circles.append(redefinedCircle)

for edge in drawable_circles[0]:
    translatedVerticies = []
    for vertex in edge.vertices:
        newVertex = (vertex[0], vertex[1] + 1, vertex[2])
        translatedVerticies.append(newVertex)
    edge.vertices = translatedVerticies

#create triangle strips
remVertices = 10

strips = []

for crossing in trefoil.crossings:
    joints = [(crossing.strands.oo, crossing.strands.iu), (crossing.strands.io, crossing.strands.ou)]
    ends = []
    for joint in joints:
        points = []
        for edge in joint:
            if crossing.coord == edge.dest:
                edge.vertices = edge.vertices[:-remVertices]
                points.append(edge.vertices[-1])
            else:
                edge.vertices = edge.vertices[remVertices:]
                points.append(edge.vertices[0])
        ends.append(points)
    centers = []
    for end in ends:
        centers.append(((end[0][0] + end[1][0])/2, (end[0][1] + end[1][1])/2, (end[0][2] + end[1][2])/2))

    deltaX = centers[1][0] - centers[0][0]
    dx = deltaX / n_edges
    deltaY = centers[1][1] - centers[0][1]
    dy = deltaY / n_edges
    deltaZ = centers[1][2] - centers[0][2]
    dz = deltaZ / n_edges

    diameters = []
    for end in ends:
        xsqr = (end[0][0] - end[1][0]) ** 2
        zsqr = (end[0][2] - end[1][2]) ** 2
        diameters.append(math.sqrt(xsqr + zsqr))

    deltaDiameter = diameters[1] - diameters[0]
    dDiameter = deltaDiameter / n_edges

    dTheta = math.pi / n_edges
    topPoint = ends[0][0] if ends[0][0][2] > ends[0][1][2] else ends[0][1]
    thetaInitial = math.atan((topPoint[2] - centers[0][2])/(topPoint[0] - centers[0][0]))
    if thetaInitial < 0:
        thetaInitial = math.pi + thetaInitial

    rail1 = []
    rail2 = []
    for i in range(0, n_edges + 1):
        r = (diameters[0] + i * dDiameter)/2
        x = centers[0][0] + i * dx
        y = centers[0][1] + i * dy
        z = centers[0][2] + i * dz
        theta1 = thetaInitial + i * dTheta
        theta2 = theta1 + math.pi
        rail1.append((r*math.cos(theta1) + x, y, r*math.sin(theta1) + z))
        rail2.append((r*math.cos(theta2) + x, y, r*math.sin(theta2) + z))
    strips.append((rail1, rail2))

# draw circles
vertexLists = []
triangleLists = []
for circle in drawable_circles:
    vertexList = []
    triangleList = []

    for edge in circle:
        vertexList += edge.vertices

    for i in range(1, len(vertexList)-1):
        triangleList.append((0, i, i+1))

    vertexLists.append(vertexList)
    triangleLists.append(triangleList)

file_name = "trefoil.obj"
output_file = open(file_name, "w")

addendums = [1]
for vertexList in vertexLists:
    addendums.append(addendums[-1] + len(vertexList))
    for vertex in vertexList:
        vertString = f"v {vertex[0]} {vertex[1]} {vertex[2]}\n"
        output_file.write(vertString)
finalAddendum = addendums[-1]

i = 0
for triangleList in triangleLists:
    for tri in triangleList:
        if i % 2 == 0 :
            triString = f"f {tri[0] + addendums[0]} {tri[1] + addendums[0]} {tri[2] + addendums[0]}\n"
        else:
            triString = f"f {tri[2] + addendums[0]} {tri[1] + addendums[0]} {tri[0] + addendums[0]}\n"
        output_file.write(triString)
        # backTriString = f"f {tri[2] + addendums[0]} {tri[1] + addendums[0]} {tri[0] + addendums[0]}\n"
        # output_file.write(backTriString)
    i += 1
    addendums.pop(0)

#draw tri strips

stripVertexLists = []
stripTriangleLists = []
for strip in strips:
    stripVertexList = []
    stripTriangleList = []

    for rail in strip:
        stripVertexList += rail

    offset = len(strip[0])
    for i in range(len(strip[0]) - 1):
        tri1 = (i, offset + i + 1,  offset + i)
        tri2 = (i,  i + 1,  offset + i + 1)
        stripTriangleList += [tri1, tri2]

    stripVertexLists.append(stripVertexList)
    stripTriangleLists.append(stripTriangleList)

stripAddendums = [finalAddendum]

for stripVertexList in stripVertexLists:
    stripAddendums.append(stripAddendums[-1] + len(stripVertexList))
    for vertex in stripVertexList:
        vertString = f"v {vertex[0]} {vertex[1]} {vertex[2]}\n"
        output_file.write(vertString)

for stripTriangleList in stripTriangleLists:
    for tri in stripTriangleList:
        triString = f"f {tri[0] + stripAddendums[0]} {tri[1] + stripAddendums[0]} {tri[2] + stripAddendums[0]}\n"
        output_file.write(triString)
        # backTriString = f"f {tri[2] + stripAddendums[0]} {tri[1] + stripAddendums[0]} {tri[0] + stripAddendums[0]}\n"
        # output_file.write(backTriString)
    stripAddendums.pop(0)

output_file.close()
