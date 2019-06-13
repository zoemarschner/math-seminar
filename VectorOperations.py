#---defines methods for manipulating vectors/segments---#

def midPoint(segment):
    return [(p1 + p2) / 2 for p1, p2 in zip(segment[0], segment[1])]

def length(segment):
    return magnitude(createVector(segment[0], segment[1]))

def normalize(vector):
    dist = magnitude(vector)
    return [comp/dist for comp in vector]

def magnitude(vector):
    dist = 0
    for comp in vector:
        dist += comp ** 2
    return dist ** 0.5

def createVector(fromPoint, toPoint):
    return [tp - fp for fp, tp in zip(fromPoint, toPoint)]

def constMult(vector, k):
    return [comp*k for comp in vector]

def vectorSum(vector1, vector2):
    return [v1 + v2 for v1, v2 in zip(vector1, vector2)]

#crosses two lists/tuples
def crossProduct(v1, v2):
    return [v1[1]*v2[2] - v1[2]*v2[1], v1[2]*v2[0] - v1[0]*v2[2], v1[0]*v2[1] - v1[1]*v2[0]]
