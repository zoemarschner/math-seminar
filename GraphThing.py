import json
import sys
import tkinter as tk
from knot import *

#set to false if >2 intersection per point is okay 
onlyTwoLoops = True

isValid = True
isClosed = False
pointSize = 25
pointNum = 0
points = {}
black, white, red = '#000000', '#FFFFFF', '#FF0000'

#creates a line between last point and seconed to last point in points
def line():
	if pointNum >= 1:
		x0, y0 = points['p' + str(pointNum - 1)]['x'], points['p' + str(pointNum - 1)]['y']
		x1, y1 = points['p' + str(pointNum)]['x'], points['p' + str(pointNum)]['y']
		canvas.create_line(x0, y0, x1, y1, width = 3)

#generate python
def placePoint(event):
	x, y = event.x, event.y
	global isClosed, isValid
	
	#get nearest point in range
	nearestPoint = pointNearPoint(x, y)
	
	#checks if there is no nearest point
	if nearestPoint == None:
		#if no nearest point add a new point
		canvas.create_oval(x - (pointSize / 2), y - (pointSize / 2), x + (pointSize / 2), y + (pointSize / 2), outline = black, fill = white, width = 2)
		points['p' + str(pointNum)] = {'x':x, 'y':y, 'used':0, 'index':pointNum, 'otherpoint': None}
		isClosed = False
	else:
		#check if more than 1 interesection at point
		if onlyTwoLoops:		
			if (points[nearestPoint]['used'] == 1) and (points[nearestPoint]['index'] != 0):
				isValid = False
		#check if valid loop
		if (pointNum - points[nearestPoint]['index']) <= 2:
			isValid = False
			print(isValid)
				
		x = points[nearestPoint]['x']
		y = points[nearestPoint]['y']
		points['p' + str(pointNum)] = {'x':x, 'y':y, 'used':1, 'index':pointNum, 'otherpoint':points[nearestPoint]['index']}
		points[nearestPoint]['used'] = 1
		points[nearestPoint]['otherpoint'] = pointNum
		#recolour point
		canvas.create_oval(x - (pointSize / 2), y - (pointSize / 2), x + (pointSize / 2), y + (pointSize / 2), outline = red, fill = white, width = 2)
		#check if loop is closed
		if points[nearestPoint]['index'] == 0:
			isClosed = True
		else:
			isClosed = False
	
	line()
	incrementPointNum()
	
#increment global variable
def incrementPointNum():
	global pointNum
	pointNum += 1

#checks if a point is near another point
def pointNearPoint(x, y):
	for point in points:
		dist = (x - points[point]['x']) ** 2 + (y - points[point]['y']) ** 2
		if dist < (pointSize) ** 2:
			return point
	return None

#check if valid and output as Json
def output():
	print(isValid)
	if isValid and isClosed:
		print('points:')
		print(json.dumps(points))
		knotObj = genKnot()
		print(knotObj)
		redrawknot()
		return knotObj
	else:
		print("invalid graph")
		return None

# redraws points with crossings
# connects points with bezier curves
def redrawknot():
	crossingPoints = []
	canvas.delete('all')
	
	# finds points to redraw
	for p in points:
		if points[p]["otherpoint"] != None and not points[p]["otherpoint"] in crossingPoints:
			# draw crossing
			x = points[p]['x']
			y = points[p]['y']
			canvas.create_oval(x - (pointSize / 2), y - (pointSize / 2), x + (pointSize / 2), y + (pointSize / 2), outline = black, fill = white, width = 1)

	# finds slope for each point
	for x in range (0, pointNum-1,1):
		if x+1 < pointNum-1:
			nx = x+1
		else:
			nx = 1
		if x-1 >= 0:
			px = x-1
		else:
			px = pointNum-1
		p = points["p"+str(x)]
		np = points["p"+str(nx)]
		pp = points["p"+str(px)]
		p["dx"] = np["x"] - pp["x"]  
		p["dy"] = np["y"] - pp["y"]
	
	# makes a bezier curve
	for x in range (0, pointNum-1,1):
		if x+1 < pointNum-1:
			nx = x+1
		else:
			nx = 0
		p = points["p"+str(x)]
		np = points["p"+str(nx)]
		d = 4
		x0 = p["x"]
		y0 = p["y"]
		x1 = p["x"] + p["dx"]/d
		y1 = p["y"] + p["dy"]/d
		x2 = np["x"] - np["dx"]/d
		y2 = np["y"] - np["dy"]/d
		x3 = np["x"]
		y3 = np["y"]
		# canvas.create_oval(x0 - (pointSize / 5), y0 - (pointSize / 5), x0 + (pointSize / 5), y0 + (pointSize / 5), outline = red, fill = white, width = 2)
		# canvas.create_oval(x1 - (pointSize / 5), y1 - (pointSize / 5), x1 + (pointSize / 5), y1 + (pointSize / 5), outline = red, fill = white, width = 2)
		# canvas.create_oval(x2 - (pointSize / 5), y2 - (pointSize / 5), x2 + (pointSize / 5), y2 + (pointSize / 5), outline = red, fill = white, width = 2)
		# canvas.create_oval(x3 - (pointSize / 5), y3 - (pointSize / 5), x3 + (pointSize / 5), y3 + (pointSize / 5), outline = red, fill = white, width = 2)
		
		xx = x0
		yy = y0
		
		res=100
		
		# formula for bezier curve
		# https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Specific_cases
		for u  in range (1,res,1):
			v = u/res
			xxx = x0*(1-v)**3 + x1*3*v*(1-v)**2 + x2*3*v**2*(1-v)+x3*v**3
			yyy = y0*(1-v)**3 + y1*3*v*(1-v)**2 + y2*3*v**2*(1-v)+y3*v**3
			canvas.create_line(xx, yy, xxx, yyy, width = 3)
			xx = xxx
			yy = yyy

#generates a knot object using points
def genKnot():
	crossingPoints = {}
	edges = []
	strands = []
	crossings = []
	
	#get crossingPoints
	for p in points:
		if points[p]["otherpoint"] != None and points[p]["otherpoint"] > points[p]["index"]:
			crossingPoints[p]={"first": points[p]["index"], "second": points[p]["otherpoint"], "oo": None, "ou": None, "io": None, "iu":None }

	tuples = []
	startPoint = points["p0"]
	crossPoint = "p0"
	crossType="o"
	tuples.append([startPoint["x"],startPoint["y"],0])
	index=1
	while index <= pointNum -1:
		name = "p" + str(index)
		tuples.append([points[name]["x"], points[name]["y"], 0])
		if points[name]["otherpoint"] != None:
			if points[name]["otherpoint"] > index:
				newcrossPoint = "p" + str(index)
				newcrossType="o"
			else:
				newcrossPoint = "p" + str(points[name]["otherpoint"])
				newcrossType="u"
			endPoint = points[name]
			e = Edge(tuples, Point(startPoint["x"], startPoint["y"], 0), Point(endPoint["x"], endPoint["y"], 0))
			# print(tuples)
			edges.append(e)
			crossingPoints[crossPoint]["o" + crossType] = e
			crossingPoints[newcrossPoint]["i" + newcrossType] = e			
			startPoint = endPoint
			crossPoint = newcrossPoint
			crossType = newcrossType
			tuples = []
			tuples.append([startPoint["x"],startPoint["y"],0])

		index = index+1
		
	for p in crossingPoints:
		s = Strands(crossingPoints[p]["oo"], crossingPoints[p]["ou"], crossingPoints[p]["io"], crossingPoints[p]["iu"])
		strands.append(s)
		name = "p" + str(crossingPoints[p]["first"])
		c = Crossing(Point(points[name]["x"], points[name]["y"], 0), s)
		crossings.append(c)
	
	return Knot(crossings)

		
#reset variables and clear canvas
def restart():
	global points, pointNum, isValid, isClosed
	points = {}
	pointNum = 0
	isValid = True
	isClosed = False
	canvas.delete('all')
	
#create window
root = tk.Tk()
root.title("Knot Generator")

#create output button and bind output() to it
outputButton = tk.Button(text='output', command=output)
outputButton.pack(side=tk.TOP, anchor=tk.W)

#create restart button and bind restart() to it
restartButton = tk.Button(text='restart ', command=restart)
restartButton.pack(side=tk.TOP, anchor=tk.W)

#creates canvas to draw on
canvas = tk.Canvas(bg=white, width=800, height=800)
canvas.pack()

#Bind placepoint action to canvas
canvas.bind('<ButtonPress-1>', placePoint)
root.mainloop()
