def createSeifertSurface(knot):
    knot.resolveOrientation()
    seifertCircles = findCircles(knot)

    genus = (len(knot.crossings) - len(seifertCircles) + 1)//2
    print(genus)

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
    seifertCircles = list(map(lambda set: list(set), seifertCircles))
    for circle in seifertCircles:
        for i in range(0, len(circle) - 1):
            edgeToFind = circle[i].dest
            for j in range(i + 1, len(circle)):
                if circle[j].origin == edgeToFind:
                    if j != i + 1:
                        temp = circle[i + 1]
                        circle[i + 1] = circle[j]
                        circle[j] = temp
                    break

    return seifertCircles
