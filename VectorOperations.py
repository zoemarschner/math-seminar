import math
#---defines methods for manipulating vectors/segments---#
#vector is represented by a list of numbers (must be length 3 for cross product)

#midpoint of two points in a list
def midPoint(segment):
    return [(p1 + p2) / 2 for p1, p2 in zip(segment[0], segment[1])]

#length of segment connecting list of two points
def length(segment):
    return magnitude(createVector(segment[0], segment[1]))

#makes vector into unit vector
def normalize(vector):
    dist = magnitude(vector)
    return [comp/dist for comp in vector]

#calculates the magnitude of vector
def magnitude(vector):
    dist = 0
    for comp in vector:
        dist += comp ** 2
    return dist ** 0.5

#creates a vector pointing from 1st point to 2nd point
def createVector(fromPoint, toPoint):
    return [tp - fp for fp, tp in zip(fromPoint, toPoint)]

#multiplies the vector by some constant k
def constMult(vector, k):
    return [comp*k for comp in vector]

#adds the vectors by component
def vectorSum(vector1, vector2):
    return [v1 + v2 for v1, v2 in zip(vector1, vector2)]

#angle between two vectors in xz plane
def angleBetween(vector1, vector2):
    dot = dotProduct(vector1, vector2)
    productMagnitudes = magnitude(vector1) * magnitude(vector2)
    cos = dot / productMagnitudes

    #prevents domain errors caused by rounding:
    if cos > 1:
        cos = 1.0
    elif cos < -1:
        cos = -1.0
    angle = math.acos(cos)
    cross = crossProduct(vector1, vector2)
    if cross[1] < 0:
        angle = 2 * math.pi - angle
    return angle

def crossProduct(vector1, vector2):
    x = vector1[1]*vector2[2] - vector1[2]*vector2[1]
    y = vector1[2]*vector2[0] - vector1[0]*vector2[2]
    z = vector1[0]*vector2[1] - vector1[1]*vector2[0]
    return [x, y, z]

def dotProduct(vector1, vector2):
    return sum([v1 * v2 for v1, v2 in zip(vector1, vector2)])
