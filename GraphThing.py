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
		return knotObj
	else:
		print("invalid graph")
		return None

#generates a knot object using points
def genKnot():
	crossingPoints = []
	edges = []
	strands = []
	crossings = []
	
	#get crossingPoints
	for p in points:
		if points[p]["otherpoint"] != None and not points[p]["otherpoint"] in crossingPoints:
			crossingPoints.append(points[p]["index"])

	#get edges
	for p in crossingPoints:
		startPoint = points["p" + str(p)]
		if p + 1 <= len(crossingPoints):
			endPoint = points["p" + str(p + 1)]
		else:
			endPoint = points["p0"]
		tuples = []
		for i in range(startPoint["index"], endPoint["index"] + 1):
			tuples.append([points["p" + str(i)]["x"], points["p" + str(i)]["y"], 0])
		edges.append(Edge(tuples, Point(startPoint["x"], startPoint["y"], 0), Point(endPoint["x"], endPoint["y"], 0)))

	

	#get strands
	for p in crossingPoints:
		oo = None
		ou = None
		io = None
		iu = None
		for e in edges:
			underIn, underOut = True, True
			if underIn:
				if e.origin.x == points["p" + str(p)]["x"] and e.origin.y == points["p" + str(p)]["y"]:
					iu = e
					underIn = False
			else:
				if e.origin.x == points["p" + str(p)]["x"] and e.origin.y == points["p" + str(p)]["y"]:
					io = e
			if underOut:
				if e.dest.x == points["p" + str(p)]["x"] and e.dest.y == points["p" + str(p)]["y"]:
					ou = e
					underIn = False
			else:
				if e.dest.x == points["p" + str(p)]["x"] and e.dest.y == points["p" + str(p)]["y"]:
					oo = e
		strands.append(Strands(oo, ou, io, iu))
	
	#build crossings
	for i in range(len(crossingPoints)):
		crossings.append(Crossing(Point(points["p" + str(crossingPoints[i])]["x"], points["p" + str(crossingPoints[i])]["y"], 0), strands[i]))
	
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
