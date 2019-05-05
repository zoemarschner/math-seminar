"""NOTES: make sure there is ONLY ONE REFERENCE to each edge and crossing"""

class Knot:
    """a Knot is described by a list of crossing_coords
        crossings is the list of all crossings in the knot"""

    def __init__(self, crossings):
        self.crossings = crossings

class Crossing:
    """Crossing is a point with four edges leaving
       coord is a Point object representing coordinates of crossing
       strands is a Strands object representing the four edges"""

    def __init__(self, coord, strands):
         self.coord = coord
         self.strands = strands

class Edge:
    """an edge is a list of verticies, going from one point to another
       verticies is a list of tuples (x, y, z) that describes the line between the two points
       origin is a Point which represents the point the verticies starts drawing from
       dest is a Point which represents the point the verticies ends drawing at
       e.g. vertices[0] should be origin and vertices[-1] should be last
       note that the vertices in the list are just tuples, since they are just used for drawing
       the origin and dest are used to compare to crossing points, so they are points"""

    def __init__(self, vertices, origin, dest):
        self.vertices = vertices
        self.origin = origin
        self.dest = dest

    def __str__(self):
        return f"{self.origin} -> {self.dest} ({id(self)})"

    def endpoints(self):
        return (self.origin, self.dest)


class Point:
    """a Point is a specific point in the graph, with coordinates in 3space (x, y, z)
       this class is used for points that have an 'identity'/will need to be compared
       the vertices used for drawing are just tuples"""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

class Strands:
    """Strands represetns the four edges that go into any crossing
       oo is the edge that goes out and over
       ou is the edge that goes out and under
       io is the edge that goes in and over
       iu is the edge that goes in and under"""

    def __init__(self, oo, ou, io, iu):
         self.oo = oo
         self.ou = ou
         self.io = io
         self.iu = iu
