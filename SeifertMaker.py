import math
from VectorOperations import *
from AlexanderPolynomial import *
import copy
STAGGER_PROPORTIONALITY_CONSTANT = 0.5

def createSeifertSurface(knot):
    knot.resolveOrientation() #make sure lists of vectors align with orientation of edges
    mutateKnot = copy.deepcopy(knot) #copy knot so that removing vertices doesn't mess stuff up

    polynomial = createAlexanderPolynomial(knot) #calcultes the alexander polynomial
    print(polynomial)

    seifertCircles = findCircles(mutateKnot) #find seifert circle

    #caluclate genus from seifert circles
    genus = (len(mutateKnot.crossings) - len(seifertCircles) + 1)//2
    print(genus)

    #move seifert circles to differnt leveles
    staggerCircles(seifertCircles)

    #create twisted strips
    strips = createBands(mutateKnot, seifertCircles)

    #draw the created shapes
    circleOutput = drawCircles(seifertCircles)
    outputString = circleOutput[0]

    stripOutput = drawStrips(strips, startIndex = circleOutput[1])
    outputString += stripOutput[0]

    writeToFile(outputString)

#----Main functions in Seifert's algorithm----#
#creates arrays of edges represeting the seifert circles
def findCircles(knot):
    seifertCircles = []
    for crossing in knot.crossings:
        #the joint represetns the two strands that are joined in the algorithm
        joints = crossing.strands.strandsJoinedinAlgorithm()
        for joint in joints:
            circlesToJoin = []
            for edge in joint:
                for circle in seifertCircles:
                    if edge in circle:
                        seifertCircles.remove(circle)
                        circlesToJoin.append(circle)
                        break
            if len(circlesToJoin) == 2:
                seifertCircles.append(circlesToJoin[0].union(circlesToJoin[1]))
            elif len(circlesToJoin) == 1:
                seifertCircles.append(circlesToJoin[0].union(joint))
            else:
                seifertCircles.append(set(joint))

    #reorder lists of edges that represent circle so that verticies are
    #in order (based on orientation)
    print(f"REORDERING CIRCLES")
    seifertCircles = list(map(lambda set: list(set), seifertCircles))
    for circle in seifertCircles:
        print(f"circle before is {[str(edge) for edge in circle ]}")
        for i in range(0, len(circle) - 1):
            edgeToFind = circle[i].dest
            for j in range(i + 1, len(circle)):
                if circle[j].origin == edgeToFind:
                    if j != i + 1:
                        print(f"switching {i} and {j}")
                        temp = circle[i + 1]
                        circle[i + 1] = circle[j]
                        circle[j] = temp
                    break
                if j == len(circle) - 1:
                    raise Exception("Circle is not connected.")
        print(f"circle after is {[str(edge) for edge in circle ]}")
    print(f"END REORDERING CIRCLES")

    return seifertCircles

def createBands(knot, seifertCircles):
    print("CREATING TRI STRIPS")
    REM_VERTICES = 5
    strips = [] #lists of pairs of bands
    for crossing in knot.crossings:
        joints = [(crossing.strands.iu, crossing.strands.oo), (crossing.strands.io, crossing.strands.ou)]
        circlesJoined = []
        ends = []

        for joint in joints:
            verticesToRemove = REM_VERTICES
            #ensure that you don't take too much of the edge off
            if (min(len(joint[0].vertices), len(joint[1].vertices)) - 2) < (REM_VERTICES * 2) :
                verticesToRemove = (min(len(joint[0].vertices), len(joint[1].vertices)) - 2) // 2

            joint[0].vertices = joint[0].vertices[:-verticesToRemove]
            joint[1].vertices = joint[1].vertices[verticesToRemove:]
            ends.append((joint[0].vertices[-1], joint[1].vertices[0]))

            for circle in seifertCircles:
                if joint[0] in circle:
                    circlesJoined.append(circle)
                    break

        #create bezier points
        midPoints = [midPoint(end) for end in ends]

        controlPoints = []
        controlPtAxisLength = length(midPoints) / 3
        endVectors = []

        for i in range(len(ends)):
            #slope in x-z plane
            slopeVec = normalize(createVector(ends[i][1], ends[i][0]))
            endVectors.append(slopeVec)
            perp = normalize([-slopeVec[2], 0, slopeVec[0]])

            #if CCW and cross negative or CW and cross positive
            orient = orientation(createVertexArray(circlesJoined[i])) #True = CCW
            cross = crossProduct(perp, slopeVec)
            print(f"at crossing {crossing.coord}, orientation is {orient}, cross initially {cross[1]}, perp is {perp}")

            if (cross[1] > 0) != orient:
                print("flip")
                perp = [-comp for comp in perp]
            print(f"cross ater {crossProduct(perp, slopeVec)[1]}, perp is {perp}")
            controlPoints.append(vectorSum(midPoint(ends[i]), constMult(perp, controlPtAxisLength)))

        #perform bezier algorithm while creating rails
        point1 = midPoints[0]
        point2 = controlPoints[0]
        point3 = controlPoints[1]
        point4 = midPoints[1]

        points = max([len(createVertexArray(circle)) for circle in circlesJoined])

        initalDiameter = length(ends[0])
        deltaDiameter = length(ends[1]) - initalDiameter
        dDiameter = deltaDiameter / (points - 1)

        dT = 1 / (points - 1)


        #linear interpolation between first end vector and second end vector
        dComponents = [(end1 - end0) / (points - 1) for end0, end1 in zip(endVectors[0], endVectors[1])]

        rail1 = []
        rail2 = []

        for pt in range(points):
            #create bezier point (P = (1−t)^3*P1 + 3(1−t)^2*tP2 +3(1−t)t^2*P3 + t^3P4)
            t = dT * pt
            bezier = lambda p1, p2, p3, p4 : ((1 - t)**3) * p1 + 3 * ((1-t)**2) * t * p2 + 3 * (1 - t) * t**2 * p3 + t**3 * p4
            bezierPt = [bezier(p1, p2, p3, p4) for p1, p2, p3, p4 in zip(point1, point2, point3, point4)]

            #create redifined coord vectors
            #w is axis perp to curve
            #u is parallel to edges at end points (linear interpolation) and points in direction of orientation
            #v is third direction
            bezierTanget = lambda p1, p2, p3, p4 : p1 * -3 * (1 - t)**2 + p2 * (-6*(1-t)*t + 3 * (1-t)**2) + p3 * (-3 * t**2 + 6*t*(1-t)) + p4 * 3 * t ** 2
            tangent = [bezierTanget(p1, p2, p3, p4) for p1, p2, p3, p4 in zip(point1, point2, point3, point4)]
            wVec = normalize(tangent)

            addComponents = [comp * pt for comp in dComponents]
            uVec = vectorSum(endVectors[0], addComponents)

            vVec = normalize(crossProduct(uVec, wVec))

            if t == 0:
                print("vectors at first point")
                print(f"ends = {ends[0]} {ends[1]}")
                print(f"midPoint = {bezierPt}")
                print(f"{wVec[0]}, {wVec[2]}")
                print(f"{uVec[0]}, {uVec[2]}")

            #use trig to find points around circle
            #initial and final points should be on u axis
            theta = -1 * math.sin(t * math.pi / 2) ** 2 * math.pi * crossing.orientation()
            r = (dDiameter * pt + initalDiameter) / 2
            #r = 1

            #points in (v, w, u)
            relPts = []
            relPts.append((r * math.sin(theta), 0, r * math.cos(theta)))
            relPts.append((r * math.sin(theta + math.pi), 0, r*math.cos(theta + math.pi)))

            #convert back to global coord system
            #points for circles are in u-v plane
            actualPts = []
            for relPt in relPts:
                diffVector = vectorSum(constMult(vVec, relPt[0]), constMult(uVec, relPt[2]))
                actualPts.append(vectorSum(diffVector, bezierPt))

            rail1.append(actualPts[0])
            rail2.append(actualPts[1])

        print(f"rail1 pt 1 is {rail1[0]}, rail2 pt1 is {rail2[0]}")
        strips.append([rail1, rail2])
    return strips

#---logic for staggering the seifert circles ----#
def staggerCircles(circles):
    intersections = findIntersections(circles)
    staggerDistance = None #only calculate this if needed, but store it once you do

    while twoDArraySum(intersections) != 0:
        baseCircle = mostIntersections(intersections)
        for i in range(len(intersections[baseCircle])):
            if intersections[baseCircle][i] == 1:
                if staggerDistance is None:
                    staggerDistance =  responsiveStaggeDistance(circles)
                raiseCircle(circles[i], staggerDistance)
                intersections[baseCircle][i] = 0
                intersections[i][baseCircle] = 0

#returns value to be used for stagger distance, related to sqaure root of the area of largest circle
def responsiveStaggeDistance(circles):
    maxArea = area(createVertexArray(circles[0]))
    maxIndex = 0
    for i in range(1, len(circles)):
        iArea = area(createVertexArray(circles[i]))
        if iArea > maxArea:
            maxArea = iArea
            maxIndex = i
    return (maxArea**0.5) * STAGGER_PROPORTIONALITY_CONSTANT

def raiseCircle(circle, amount):
    for edge in circle:
        edge.raiseEdge(amount)

#sums the values in a 2D array
def twoDArraySum(array):
    total = 0
    for row in array:
        total += sum(row)
    return total

#returns index of circle which intersects the most other circles
def mostIntersections(intersectionArray):
    maxIndex = 0
    maxIntersections = sum(intersectionArray[0])
    for i in range(1, len(intersectionArray)):
        intersections = sum(intersectionArray[i])
        if intersections > maxIntersections:
            maxIndex = i
            maxIntersections = intersections

    return maxIndex


#---logic for checking interesections----#

def findIntersections(circles):
    intersectionArray = [[0 for i in range(len(circles))] for i in range(len(circles))]

    #check each pair of circles to see whether it is enclosed in another
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            enclosed = checkEnclosed(circles[j], circles[i]) or checkEnclosed(circles[i], circles[j])
            if enclosed:
                intersectionArray[i][j] = 1
                intersectionArray[j][i] = 1

    print(intersectionArray)
    return intersectionArray

#checks whether circle1 is enclosed in circle2, with precondition that their sides never interesect
#returns true if it is enclosed
def checkEnclosed(circle1, circle2):
    point = createVertexArray(circle1)[0]
    intersections = 0
    circle2Arr = createVertexArray(circle2)
    point = None
    for pt in createVertexArray(circle1):
        if pt not in circle2Arr:
            point = pt
            break

    #if all the points are on the other circle, one will be enclosed
    if point is None:
        return True

    for i in range(len(circle2Arr)):
        p1 = circle2Arr[i]
        p2 = circle2Arr[(i + 1) % len(circle2Arr)]

        zValid = (p1[2] - point[2]) * (p2[2] - point[2]) < 0

        p1ZDist = p1[2]-point[2]
        totalZDist = p1[2] - p2[2]

        if totalZDist == 0:
            if p1ZDist == 0 and p1[0] > point[0]:
                intersections += 1
            break

        totalXDist = p1[0] - p2[0]
        p1XDist = (p1ZDist/totalZDist) * totalXDist
        xCoord = p1[0] - p1XDist
        if xCoord > point[0] and zValid:
            print(f"intersection found with segment {p1} {p2}, xCoord = {xCoord}, zValid = {zValid}")
            intersections += 1
    str = ""
    for pt in circle2Arr:
        str += f"({pt[0]},{pt[2]}),"

    print(f"{point} point has {intersections} intersections with {str}")
    return intersections % 2 != 0

#----functions for outputting obj----#

def writeToFile(string, name="knot.obj"):
    fileName = name
    outputFile = open(fileName, "w")
    outputFile.write(string)
    outputFile.close()

#returns tuple of outputString to add and new starting index
def createOutputString(vertices, relTriangles, startIndex):
    triangles = [[vertex + startIndex for vertex in triangle] for triangle in relTriangles]

    outputString = ""

    for vertex in vertices:
        outputString += f"v {vertex[0]} {vertex[1]} {vertex[2]}\n"

    for triangle in triangles:
        outputString += f"f {triangle[0]} {triangle[1]} {triangle[2]}\n"

    return (outputString, startIndex + len(vertices))


#----functions for triangulation---#

#---functions for drawing circles---#

#takes array of edges that make a circle and converts in to array of points
def createVertexArray(circle):
    vertexArray = []
    for edge in circle:
        vertices = edge.vertices
        if vertices[0] in vertexArray:
            vertices = vertices[1:]
        vertexArray += vertices
    if vertexArray[-1] == vertexArray[0]:
        vertexArray = vertexArray[:-1]
    return vertexArray

#draws an array of multiple lists of edges (used to draw seifert circles)
#returns tuple of outputString to add and new starting index
def drawCircles(disks, startIndex = 1):
    outputString = ""

    for disk in disks:
        vertices = createVertexArray(disk)

        res = drawDisk(vertices, startIndex)
        outputString += res[0]
        startIndex = res[1]

    return (outputString, startIndex)

#returns string to add to obj that will connect the list of vertices as a disk
#startIndex is the index of the first vertex added to the file by this call
#returns tuple of outputString to add and new starting index
def drawDisk(vertices, startIndex):
    triangles = createTrianglesEar(vertices)
    return createOutputString(vertices, triangles, startIndex)


#returns triangles to make a fan connceting vertices. Only works for convex polygons
def createTrianglesFan(vertices):
    triangleList = []
    for i in range(1,len(vertices)):
        triangleList.append([0, i, (i + 1) % len(vertices)])
    return triangleList

#uses ear clipping method to make triangulation of any polygon
def createTrianglesEar(vertices):
    triangleList = []
    curVertices = []

    for i in range(len(vertices)):
        curVertices.append((vertices[i], i))

    #applying ear algorithm
    while len(curVertices) != 3:
        for i in range(len(curVertices)):
            if isValidEar(i, curVertices):
                prev = curVertices[(i - 1) % len(curVertices)]
                next = curVertices[(i + 1) % len(curVertices)]
                triangleList.append((prev[1], curVertices[i][1], next[1]))
                del curVertices[i]
                break
        else:
            raise Exception("No valid ear exists")

    triangleList.append((curVertices[0][1], curVertices[1][1], curVertices[2][1]))

    return triangleList

def isValidEar(index, curVertices):
    #a vertex is valid ear (can be removed as a traingle) if
    #no points in the array are inside the triangle
    #and the vertex is concave

    prev = curVertices[(index - 1) % len(curVertices)][0]
    check = curVertices[index][0]
    next = curVertices[(index + 1) % len(curVertices)][0]
    triangle = [prev, check, next]

    #check that there are no points in triangle by using cross product
    for vertexToCheck in curVertices:
        crossProducts = []
        for i in range(len(triangle)):
            vector1 = createVector(triangle[i], triangle[(i+1) % len(triangle)])
            vector2 = createVector(triangle[i], vertexToCheck[0])
            cross = crossProduct(vector1, vector2)
            crossProducts.append(cross)

        CCW = crossProducts[0][1] > 0 and crossProducts[1][1] > 0 and crossProducts[2][1] > 0
        CW = crossProducts[0][1] < 0 and crossProducts[1][1] < 0 and crossProducts[2][1] < 0
        if CCW or CW:
            return False

    #check whether the vertex is concave
    vector1 = createVector(check, prev)
    vector2 = createVector(check, next)
    cross = crossProduct(vector1, vector2)
    if (cross[1] < 0) == orientation([vertexPair[0] for vertexPair in curVertices]):
        return False

    return True

#returns the orientation of the polygon defined by the vertex array
#True for CCW, False for CW
def orientation(vertexArray):
    return gaussAreaFormula(vertexArray) > 0

#returns are of the polygon defined by the vertex array
def area(vertexArray):
    return abs(gaussAreaFormula(vertexArray))

#gives signed area
def gaussAreaFormula(vertexArray):
    sum = 0

    for i in range(len(vertexArray)):
        v1 = vertexArray[i]
        v2 = vertexArray[(i + 1) % len(vertexArray)]
        sum += (v1[0] + v2[0])*(v2[2] - v1[2])

    return sum / 2

#---functions for drawing strips---#

#creates outputStrings for an array of multiple triangle strips
def drawStrips(strips, startIndex = 1):
    outputString = ""

    for strip in strips:
        res = drawStrip(strip, startIndex)
        outputString += res[0]
        startIndex = res[1]
    return (outputString, startIndex)

def drawStrip(strip, startIndex):
    triangles = createStripTriangles(strip)
    vertices = strip[0] + strip[1]
    return createOutputString(vertices, triangles, startIndex)

#creates traingles that draw a strip given two lists of rails
#indices are into the joined list of vertices in both strips, starting at 0
def createStripTriangles(strip):
    rail1Offset = len(strip[0])
    triangles = []

    for i in range(len(strip[0]) - 1):
        tri1 = (i, i + 1, i + rail1Offset)
        tri2 = (i + 1, i + 1 + rail1Offset, i + rail1Offset)
        triangles.append(tri1)
        triangles.append(tri2)

    return triangles
