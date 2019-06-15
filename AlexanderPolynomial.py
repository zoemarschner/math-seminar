from VectorOperations import *
from numpy.polynomial.polynomial import *
import copy

#create the alexander polynomial of the knot in the standrad form (symmetrical)
#returns tuple of string representing polynomial and the genus
def createAlexanderPolynomial(knot):
    regions = findRegions(knot)

    matrix = createMatrix(knot, regions)

    #rem adjacent columns
    #just always removes first column and one adjacent to it
    for i in range(1, len(regions)):
        if len(set(regions[0]).intersection(set(regions[i]))) > 0:
            for row in matrix:
                del row[i]
                del row[0]
            break

    polynomial = determinant(matrix)
    return standardize(polynomial)

#used in finding region, a strand and the information of whether it is over/under
class RelativeStrand:
    def __init__(self, edge, out, over):
         self.edge = edge
         self.over = over
         self.out = out

    def __str__(self):
        return f"{self.edge}, {'out' if self.out else 'in'} & {'over' if self.over else 'under'}"


def createRelativeStrands(strands):
    result = []
    result.append(RelativeStrand(strands.oo, True, True))
    result.append(RelativeStrand(strands.io, False, True))
    result.append(RelativeStrand(strands.ou, True, False))
    result.append(RelativeStrand(strands.iu, False, False))

    return result
#returns list of lists of edges that form regions in the knot
def findRegions(knot):
    #set of frozen sets of edges
    regions = []

    for crossing in knot.crossings:
        relStrands = createRelativeStrands(crossing.strands)

        #loops over each strand at crossing
        for strand in relStrands:
            thisStrandVec = crossing.strands.getVector(strand.edge, strand.out)

            #this strand can connect to either of the nextStrands to form a region
            nextStrands = [nextStrand for nextStrand in relStrands if nextStrand.over != strand.over]

            sortedNextStrands = [(angleBetween(thisStrandVec, crossing.strands.getVector(otherStrand.edge, otherStrand.out)), otherStrand) for otherStrand in nextStrands]
            sortedNextStrands.sort() #sorts the strands to be connected by their angle

            for i in range(len(sortedNextStrands)): #i here represents left or right
                nextStrand = sortedNextStrands[i][1] #nextStrand holds strand that we are looking for
                                                     #with reference frame of curCrossing
                region = [strand.edge]
                curCrossing = crossing

                while nextStrand.edge != strand.edge: #move around regions until you encounter same strand
                    region.append(nextStrand.edge)

                    for nextCrossing in knot.crossings: #find the other crossing that involves nextStrand (can be same crossing)

                        #crossing should include strand that is the same edge but opposite outness
                        nextCrossingStrands = createRelativeStrands(nextCrossing.strands)
                        for possibleStrand in nextCrossingStrands:
                            if possibleStrand.edge == nextStrand.edge and possibleStrand.out != nextStrand.out:
                                nextStrandThisCrossing = possibleStrand #the nextstrand represented relative to the new crossing
                                break #found correct crossing, continue with the crossing for loop
                        else:
                            continue #no strands in crossing are the desired one, skip this crossing and continue in outer loop

                        #handles logic of choosing which strands to join next
                        #note case of twisted unknot where same strand can occur twice at a crossing
                        #however, if same strand occurs twice it will be once as over and once as under

                        newNextStrands = [newNextStrand for newNextStrand in nextCrossingStrands if newNextStrand.over != nextStrandThisCrossing.over]

                        nextStrandVec = nextCrossing.strands.getVector(nextStrand.edge, nextStrandThisCrossing.out)
                        sortedNewNextStrands = [(angleBetween(nextStrandVec, nextCrossing.strands.getVector(otherStrand.edge, otherStrand.out)), otherStrand) for otherStrand in newNextStrands]
                        sortedNewNextStrands.sort()

                        nextStrand = sortedNewNextStrands[i][1]
                        curCrossing = nextCrossing

                        break

                for existingRegion in regions:
                    if set(region) == set(existingRegion):
                        break
                else:
                    regions.append(region)

    return list(regions)

#creates the matrix for the given knot with regions already found
#returns a 2D array of numpy polynomial objects
def createMatrix(knot, regions):
    matrix = []
    #polynomials in order: iu-oo, oo-ou, ou-io, io-iu
    polynomialsPositive = [Polynomial((1)), Polynomial((-1)), Polynomial((0, 1)), Polynomial((0, -1))]
    polynomialsNegative = list(reversed(polynomialsPositive))

    for crossing in knot.crossings:
        s = crossing.strands
        #these are the pairs of edges that correspond to the polynomials defined above
        adjacentEdges = [[s.iu, s.oo], [s.oo, s.ou], [s.ou, s.io], [s.io, s.iu]]

        row = [Polynomial((0)) for region in regions]
        orientation = crossing.orientation()

        for index in range(len(adjacentEdges)):
            for i in range(len(regions)):
                if set(adjacentEdges[index]) <= set(regions[i]):
                    edgeIndex = regions[i].index(adjacentEdges[index][0])
                    before = regions[i][(edgeIndex - 1) % len(regions[i])] == adjacentEdges[index][1]
                    after = regions[i][(edgeIndex + 1) % len(regions[i])] == adjacentEdges[index][1]
                    if before or after: #this region contains both the edges
                        row[i] = polynomialsPositive[index] if (orientation > 0) else polynomialsNegative[index]
                        break

        matrix.append(row)

    return matrix

#takes the determinant of square matrix of polynomial objects
def determinant(matrix):
    if len(matrix) == 1: #base case of 1x1, only called if initally 1x1
        return matrix[0][0]

    if len(matrix) == 2: #base case, 2x2 matrix
        return polysub(polymul(matrix[0][0],  matrix[1][1]), polymul(matrix[0][1],  matrix[1][0]))

    results = []
    for i in range(len(matrix)):
        #remove one row and column
        recurseMatrix = copy.deepcopy(matrix[1:])
        for row in recurseMatrix:
            del row[i]

        #sign to multiply by alternates
        if (i % 2 != 0):
            mult = polymul(Polynomial((-1)), matrix[0][i])
        else:
            mult = matrix[0][i]

        results.append(polymul(mult, determinant(recurseMatrix)))

    sum = results[0]
    for j in range(1, len(results)):
        sum = polyadd(sum, results[j])

    return sum

#takes alexander polynomial and puts it in symetric form
#(precondition is that polynomial is symmetric, which is theorem for alexander polynomial)
#returns tuple of string representing polynomial and the genus calculted from polynomial
def standardize(polynomial):
    if not isinstance(polynomial, Polynomial):
        polynomial = polynomial[0]

    coefficients = polynomial.coef.tolist()

    #remove zeros leading zeros
    while(coefficients[0] == 0 and len(coefficients) > 1): #while need to remove zeros
        del coefficients[0]

    #negates all coefficents if nessecary so that largest coefficent is positive
    if coefficients[-1] < 0:
        coefficients = [-coef for coef in coefficients]


    deg = len(coefficients) - 1 #"degree" of polynomial, always even
    lowestPower = - deg // 2 #so that it is symmetric laurent polynomial
    genus = deg // 2 #genus is bounded below by half the degree


    #formats the polynomial as a string
    polynomialString = ""
    for j in reversed(range(len(coefficients))):
        power = lowestPower + j

        #t string is t to the power of some coefficent
        if coefficients[j] == 0:
            continue

        if power == 0:
            tString = ""
        else:
            tString = f"t^{str(power)}"

        #mult string is coefficent multipled by poynomail
        if (tString != "") and (abs(coefficients[j]) == 1):
            multString = ""
        else:
            multString = str(int(abs(coefficients[j])))

        termString = multString + tString

        if coefficients[j] < 0:
            termString = "- " + termString
        elif j != len(coefficients) - 1:
            termString = "+ " + termString

        if j != 0:
            termString += " "

        polynomialString += termString

    if polynomialString == "":
        polynomialString = "0"

    return(polynomialString, genus)
