import json
import math
import sys
import tkinter as tk
from knot import *
import SeifertMaker


# global varibales

isValid = True
isClosed = False
isFirstPointCrossing = False
isFinished = False

pointSize = 25
pointDistanse = 10;


pointNum = 0
crossingNum = 0
lastCrossing = 0
points = {}
crossings = {}

refinedPoints = {}
refinedPointsNum = 0

edges = []

black, white, red = '#000000', '#FFFFFF', '#FF0000'






#checks if a point is near another point
def pointNearPoint(x, y):
	for point in points:
		dist = (x - points[point]['x']) ** 2 + (y - points[point]['y']) ** 2
		if dist < (pointSize) ** 2:
			return point
	return None


#checks if a point is near crossing point
def crossingNearPoint(x, y):
	for point in crossings:
		dist = (x - crossings[point]['x']) ** 2 + (y - crossings[point]['y']) ** 2
		if dist < (pointSize) ** 2:
			return point
	return None



# place a new point
def addPoint(x,y):
	global isClosed, isValid, isFirstPointCrossing
	global pointNum, crossingNum

	nearestPoint = pointNearPoint(x, y)
	if nearestPoint == None:
		#if no nearest point add a new point

		# add point to the list
		points['p' + str(pointNum)] = {'x':x, 'y':y, 'used':0, 'index':pointNum, 'otherpoint': None}
		isClosed = False

		#draw circle
		canvas.create_oval(x - (pointSize / 2), y - (pointSize / 2), x + (pointSize / 2), y + (pointSize / 2), outline = black, fill = white, width = 2)

		#draw line
		if pointNum >= 1:
			x0, y0 = points['p' + str(pointNum - 1)]['x'], points['p' + str(pointNum - 1)]['y']
			canvas.create_line(x0, y0, x, y, width = 3)

		# increase num of points
		# incrementPointNum()
		pointNum += 1

	else:
		# this is a crossing
		# get index of other point
		np = points[nearestPoint]['index']
		x = points[nearestPoint]['x']
		y = points[nearestPoint]['y']

		if points[nearestPoint]['used'] == 0:
			# add point to the list
			points['p' + str(pointNum)] = {'x':x, 'y':y, 'used':1, 'index':pointNum, 'otherpoint': np, 'crossing': crossingNum}

			# draw line
			x0, y0 = points['p' + str(pointNum - 1)]['x'], points['p' + str(pointNum - 1)]['y']
			canvas.create_line(x0, y0, x, y, width = 3)

			if np+2 == pointNum:
				isValid= False
				#recolour point
				canvas.create_oval(x - (pointSize / 2), y - (pointSize / 2), x + (pointSize / 2), y + (pointSize / 2), outline = red, fill = red, width = 2)
			else:
				#recolour point
				canvas.create_oval(x - (pointSize / 2), y - (pointSize / 2), x + (pointSize / 2), y + (pointSize / 2), outline = red, fill = white, width = 2)

			# modify nearestpoint
			points[nearestPoint]['used'] = 1
			points[nearestPoint]['otherpoint'] = pointNum
			points[nearestPoint]['crossing'] = crossingNum

			# add crossing
			crossings['c' + str(crossingNum)] = {'x':x, 'y':y, 'index':crossingNum, 'firstPoint':np, 'secondPoint': pointNum,"oo": None, "ou": None, "io": None, "iu":None}
			#incrementCrossingNum()
			crossingNum += 1

			if np == 0:
				isClosed = True
			else:
				isClosed = False
			#	setLastCorssing()

			# increase num of points
			#incrementPointNum()
			pointNum += 1


		else:
			if np != 0:
				#invalid loop
				isValid = False

				# add point to the list
				points['p' + str(pointNum)] = {'x':x, 'y':y, 'used':1, 'index':pointNum, 'otherpoint': np, 'crossing': crossingNum}

				# draw line
				x0, y0 = points['p' + str(pointNum - 1)]['x'], points['p' + str(pointNum - 1)]['y']
				canvas.create_line(x0, y0, x, y, width = 3)

				#draw circle
				canvas.create_oval(x - (pointSize / 2), y - (pointSize / 2), x + (pointSize / 2), y + (pointSize / 2), outline = black, fill = red, width = 2)

				# increase num of points
				# incrementPointNum()
				pointNum += 1
			else:
				# closing the loop at the initial point which is also crossing

				# add point to the list
				points['p' + str(pointNum)] = {'x':x, 'y':y, 'used':2, 'index':pointNum, 'otherpoint': np, 'crossing': points['p0']['crossing']}

				# draw line
				x0, y0 = points['p' + str(pointNum - 1)]['x'], points['p' + str(pointNum - 1)]['y']
				canvas.create_line(x0, y0, x, y, width = 3)

				isClosed = True
				isFirstPointCrossing = True
				# increase num of points
				# incrementPointNum()
				pointNum += 1

				# finish drawing....
				finishDraw()






# redraw the knot
def redrawKnot():
	# erase everything
	crossingPoints = []
	canvas.delete('all')

	# draw crossings
	for c in crossings:
		# draw crossing
		x = crossings[c]['x']
		y = crossings[c]['y']
		canvas.create_oval(x - (pointSize / 2), y - (pointSize / 2), x + (pointSize / 2), y + (pointSize / 2), outline = black, fill = white, width = 1)

	# draw points on the edges
#	for c in refinedPoints:
#		x = refinedPoints[c]['x']
#		y = refinedPoints[c]['y']
#		canvas.create_oval(x - 2, y - 2, x + 2, y + 2, outline = black, fill = black, width = 0.2)

	# draws  bezier curves
	for x in range (0, refinedPointsNum-1,1):
		p = refinedPoints["rp"+str(x)]
		np = refinedPoints["rp"+str(p['np'])]

		# check if you need to remove parts of the curve
		if p['used'] == 0:
			a=0
		else:
			if crossings['c'+str(p['crossing'])]['firstPoint'] == p['old']:
				a=0
			else:
				a=0.75

		if np['used'] == 0:
			b=1
		else:
			if crossings['c'+str(np['crossing'])]['firstPoint'] == np['old']:
				b=1
			else:
				b=0.25

		drawBezierCurve(p['x0'],p['y0'],p['x1'],p['y1'],p['x2'],p['y2'],p['x3'],p['y3'],a,b)



# finds slope for each point and computes the lenghts of Bezier curves
def computeTangentsAndLenghts():
	# find the previous and next point
	for x in range (0, pointNum,1):
		p = points["p"+str(x)]
#		print(p)
		if x+2 < pointNum:
			p['np'] = x+1
		else:
			p['np'] = 0
		if x-1 >= 0:
			p['pp'] = x-1
		else:
			p['pp'] = pointNum-2
		np = points["p"+str(p['np'])]
		pp = points["p"+str(p['pp'])]
		# computes the difference
		p["dx"] = np["x"] - pp["x"]
		p["dy"] = np["y"] - pp["y"]
#		print(p)

	# finds the controll points for the Bezier curves
	for x in range (0, pointNum-1,1):
		p = points["p"+str(x)]
		np = points["p"+str(p['np'])]
		# this controls the smoothness...
		d = 4
		# set up control points
		p['x0'] = p["x"]
		p['y0'] = p["y"]
		p['x1'] = p["x"] + p["dx"]/d
		p['y1'] = p["y"] + p["dy"]/d
		p['x2'] = np["x"] - np["dx"]/d
		p['y2'] = np["y"] - np["dy"]/d
		p['x3'] = np["x"]
		p['y3'] = np["y"]

		# get the lenght
		p['len'] = lenghtsOfBezierCurve(p['x0'],p['y0'],p['x1'],p['y1'],p['x2'],p['y2'],p['x3'],p['y3'])
#		print(p)



# compute point on Bezier curve
def pointOnBezierCurve(x0,y0,x1,y1,x2,y2,x3,y3,v):
	x = x0*(1-v)**3 + x1*3*v*(1-v)**2 + x2*3*v**2*(1-v)+x3*v**3
	y = y0*(1-v)**3 + y1*3*v*(1-v)**2 + y2*3*v**2*(1-v)+y3*v**3
	return x,y

# computes lenght of Bezeier curve
def lenghtsOfBezierCurve(x0,y0,x1,y1,x2,y2,x3,y3):
	xx = x0
	yy = y0
	l = 0
	# number of points to approiximate -- 500 is an over kill
	res=500
	for u  in range (1,res,1):
		v = u/res
		xxx,yyy = pointOnBezierCurve(x0,y0,x1,y1,x2,y2,x3,y3,v)
		l += math.sqrt( (xx-xxx)**2 + (yy-yyy)**2 )
		xx = xxx
		yy = yyy
	return l

# draw part of Bezier Curve
def drawBezierCurve(x0,y0,x1,y1,x2,y2,x3,y3,a,b):

	xx,yy = pointOnBezierCurve(x0,y0,x1,y1,x2,y2,x3,y3,a)
	#  number of segments -- we already added extra points so there is no need of large numbers
	res=10
	for u  in range (int(a*res+1),int(b*res),1):
		v = u/res
		xxx,yyy = pointOnBezierCurve(x0,y0,x1,y1,x2,y2,x3,y3,v)
		canvas.create_line(xx, yy, xxx, yyy, width = 3, capstyle = 'round')
		xx = xxx
		yy = yyy


# add extra points
def refinePoints():
	global refinedPointsNum
	# the average distance between points
	if isFirstPointCrossing:
		i=0
	else:
		i=crossings['c0']['firstPoint']

	refinedPointsNum = 0

	while i < pointNum-1:
		p = points['p'+str(i)]
		refinedPoints['rp'+str(refinedPointsNum)] = {'x':p['x'], 'y':p['y'], 'used':p['used'], 'old':i}
		if p['used']!=0:
			refinedPoints['rp'+str(refinedPointsNum)]['crossing']= p['crossing']
		refinedPointsNum += 1
		morePoints = int(p['len'] / pointDistanse)
		# adds extra points if necessary
		for j in range(1,morePoints,1):
			x,y = pointOnBezierCurve(p['x0'],p['y0'],p['x1'],p['y1'],p['x2'],p['y2'],p['x3'],p['y3'], j/morePoints)
			refinedPoints['rp'+str(refinedPointsNum)] = {'x':x, 'y':y, 'used':0,'old':-1}
			refinedPointsNum += 1
		i +=1
	if 	isFirstPointCrossing:
		p = points['p0']
		refinedPoints['rp'+str(refinedPointsNum)] = {'x':p['x'], 'y':p['y'], 'used':p['used'], 'old':0, 'crossing': p['crossing']}
		refinedPointsNum += 1
	else:
		i=0
		while i < crossings['c0']['firstPoint']:
			p = points['p'+str(i)]
			refinedPoints['rp'+str(refinedPointsNum)] = {'x':p['x'], 'y':p['y'], 'used':p['used'],'old':i}
			if p['used']!=0:
				refinedPoints['rp'+str(refinedPointsNum)]['crossing']= p['crossing']
			refinedPointsNum += 1
			morePoints = int(p['len'] / pointDistanse)
			# adds extra points if necessary
			for j in range(1,morePoints,1):
				x,y = pointOnBezierCurve(p['x0'],p['y0'],p['x1'],p['y1'],p['x2'],p['y2'],p['x3'],p['y3'], j/morePoints)
				refinedPoints['rp'+str(refinedPointsNum)] = {'x':x, 'y':y, 'used':0,'old':-1}
				refinedPointsNum += 1
			i += 1
		p = points['p'+str(i)]
		refinedPoints['rp'+str(refinedPointsNum)] = {'x':p['x'], 'y':p['y'], 'used':p['used'],'old':i, 'crossing': p['crossing']}
		refinedPointsNum += 1

#	for r in refinedPoints:
#		print(r,refinedPoints[r])

	# recomputes the adjecent points and slopes
	for x in range (0, refinedPointsNum-1,1):
		p = refinedPoints['rp'+str(x)]
		if x+2 < refinedPointsNum:
			p['np'] = x+1
		else:
			p['np'] = 0
		if x-1 >= 0:
			p['pp'] = x-1
		else:
			p['pp'] = refinedPointsNum-2
		np = refinedPoints['rp'+str(p['np'])]
		pp = refinedPoints['rp'+str(p['pp'])]
		p["dx"] = np["x"] - pp["x"]
		p["dy"] = np["y"] - pp["y"]
#		print(p)

	# recomputes the control points
	for x in range (0, refinedPointsNum-1,1):
		p = refinedPoints["rp"+str(x)]
		np = refinedPoints["rp"+str(p['np'])]
		d = 4
		# set up control points
		p['x0'] = p["x"]
		p['y0'] = p["y"]
		p['x1'] = p["x"] + p["dx"]/d
		p['y1'] = p["y"] + p["dy"]/d
		p['x2'] = np["x"] - np["dx"]/d
		p['y2'] = np["y"] - np["dy"]/d
		p['x3'] = np["x"]
		p['y3'] = np["y"]


# construct the edges and attach them to the crossings
def getEdges():
	tuples = []
	startPoint = refinedPoints["rp0"]
	crossPoint = 'c'+str(startPoint["crossing"])
	crossType="u"
	tuples.append([startPoint["x"], 0, startPoint["y"]])
	index=1
	while index <= refinedPointsNum -1:
		name = "rp" + str(index)
		p = refinedPoints[name]
		tuples.append([p["x"], 0, p["y"]])
		if p["used"] == 1:
			# we have finshed a whole edge...
			newcrossPoint = 'c'+str(p["crossing"])
			# gets the type of corssing
			if crossings[newcrossPoint]['firstPoint'] == p['old']:
				newcrossType="u"
			else:
				newcrossType="o"

			endPoint = refinedPoints[name]
			e = Edge(tuples, Point(startPoint["x"], 0, startPoint["y"]), Point(endPoint["x"], 0,  endPoint["y"]))
			# print(tuples)
			edges.append(e)
			# links the edge to the corssings
			crossings[crossPoint]["o" + crossType] = e
			crossings[newcrossPoint]["i" + newcrossType] = e
			startPoint = endPoint
			crossPoint = newcrossPoint
			crossType = newcrossType
			tuples = []
			tuples.append([startPoint["x"],0, startPoint["y"]])

		index = index+1

# event handler for drawing the knot
def newPlacePoint(event):
	addPoint(event.x, event.y)

# event handler for flipping the corssings
def flipCrossing(event):
	#first find the corssing
	cr = crossingNearPoint(event.x, event.y)
	if cr != None:
		# swap amlost everything attached to the corssing
		c = crossings[cr]
#		changeCrossing(cr)
		f = c['firstPoint']
		s = c['secondPoint']
		c['firstPoint'] = s
		c['secondPoint'] = f
		f = c['oo']
		s = c['ou']
		c['oo'] = s
		c['ou'] = f
		f = c['io']
		s = c['iu']
		c['io'] = s
		c['iu'] = f

		# redraw the knot
		redrawKnot()

# switch from drawing to flipping crossings also checks if the knot is valid
def finishDraw():
	global isFinished
	if isValid and isClosed:
		if not isFinished:
			computeTangentsAndLenghts()
			if isFirstPointCrossing == False:
				# remove the first crossing
				points['p0']['used']=0
				points['p'+str(pointNum-1)]['used'] = 0
				c = 'c'+str(points['p0']['crossing'])
				del crossings[c]

			refinePoints()
			getEdges()
			redrawKnot()
			canvas.bind('<ButtonPress-1>', flipCrossing)
			isFinished = True
	else:
		print("invalid graph")
		restart()

# construct the knot object and print it
def outputKnot():
	strands = []
	cross = []

	for c in crossings:
		s = Strands(crossings[c]["oo"], crossings[c]["ou"], crossings[c]["io"], crossings[c]["iu"])
		strands.append(s)
#		print(s)
		cr = Crossing(Point(crossings[c]["x"], 0,  crossings[c]["y"]), s)
		cross.append(cr)
#		print(cr)


	knotObj =  Knot(cross)
	printEdges()
	printKnot(knotObj)
	SeifertMaker.createSeifertSurface(knotObj)
	return knotObj

# prints knot
def printKnot(knotObj):
	print("--- Knot Begin  ---")
	print(knotObj)
	print("--- Knot End    ---")

# prints edges
def printEdges():
	i = 0
	print("--- Edges Begin ---")
	while i < len(edges):
		print(id(edges[i]), edges[i].vertices)
		i +=1
	print("--- Edges End   ---")

#reset variables and clear canvas
def restart():
	global points, crossings, pointNum, crossingNum, edges, refinedPoints,refinedPointsNum
	global isValid, isClosed, isFirstPointCrossing, isFinished

	points = {}
	crossings = {}
	pointNum = 0
	crossingNum = 0
	refinedPoints = {}
	refinedPointsNum = 0
	edges=[]
	isValid = True
	isClosed = False
	isFirstPointCrossing = False
	isFinished = False
	canvas.bind('<ButtonPress-1>', newPlacePoint)
	canvas.delete('all')
	print("Restart")







#create window
root = tk.Tk()
root.title("Knot Generator")

#create output button and bind output() to it
finishButton = tk.Button(text='Finish Drawing', command=finishDraw)
finishButton.pack(side=tk.TOP, anchor=tk.W)

#create output button and bind output() to it
outputButton = tk.Button(text='Output Knot', command=outputKnot)
outputButton.pack(side=tk.TOP, anchor=tk.W)

#create restart button and bind restart() to it
restartButton = tk.Button(text='Restart', command=restart)
restartButton.pack(side=tk.TOP, anchor=tk.W)

#creates canvas to draw on
canvas = tk.Canvas(bg=white, width=800, height=800)
canvas.pack()

#Bind placepoint action to canvas
canvas.bind('<ButtonPress-1>', newPlacePoint)
root.mainloop()
