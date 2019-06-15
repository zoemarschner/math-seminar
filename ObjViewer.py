import pyglet
from pyglet.gl import *
from sys import argv, stdin
from VectorOperations import *
import re

rx = ry = rz = 0

#global variables

#defines colors to be used, first index for light mode and second index for dark mode
CLEAR_COLORS = [(1, 1, 1, 1), (33/255, 33/255, 33/255, 1)]
BACK_COLORS = [(35/255, 39/255, 255/255, 1), (35/255, 39/255, 255/255, 1)]
FRONT_COLORS = [(255/255, 17/255, 17/255, 1), (255/255, 17/255, 17/255, 1)]

mode = 0 #0 for light mode, 1 for dark mode

blackAndWhite = False
BACK_BW = (.3, .3, .3, 1)
FRONT_BW = (.7, .7, .7, 1)

openFile = False

#---functions to be interfaced with---#
#to use program call these functions or run program with fileName as an argument

#pass fileName of obj file
def renderObjFile(fileName):
    openFile = True

    file = open(fileName)
    if file.mode == 'r':
        string = file.read()

    render(string)

#pass string contents of obj file
def renderObjString(string):
    openFile = False

    render(string)

#---rendering functions---#
def render(string):
    config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True,)
    window = pyglet.window.Window(resizable=True, config=config)

    @window.event
    def on_resize(width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40., width / float(height), .1, 1000.) #fov angle, aspect, znear, zfar
        glMatrixMode(GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    @window.event
    def on_draw():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, -1.75)
        glRotatef(rz, 0, 0, 1)
        glRotatef(rx, 1, 0, 0)
        glRotatef(ry, 0, 1, 0)
        batch.draw()

    #for handeling rotation
    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        global rx, ry, rz
        #y increased => decrease rx
        #x increased => increase ry
        rx -= dy
        ry += dx

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == 108: #character = l; toggle dark mode
            global mode
            mode = 0 if mode == 1 else 1
            updateColors()
        elif symbol == 98: #character = b; toggle black and white
            global blackAndWhite
            blackAndWhite = not blackAndWhite
            updateColors()
        elif symbol == 119: #character = w; write string to file (if opened from string)
            if not openFile:
                writeToFile(string)

    setup()
    batch = pyglet.graphics.Batch()
    parseObj(string, batch)

    pyglet.app.run()


def setup():
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE) #draws the back of triangle also

    glEnable(GL_LIGHTING) #turn on lighting
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE) #enables two sided lighting

    #set properties of lights
    #diffuse is base color, specular is color of highlight
    glLightfv(GL_LIGHT0, GL_POSITION, vec(-1, 1.5, 0, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(.8, .8, .8, 1))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(1.5, -2.5, 0, 1))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(0.2, 0.2, 0.2, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(0.2, 0.2, 0.2, 1))

    #set properties of materials
    updateColors()
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

#create ctype array
def vec(*args):
    return (GLfloat * len(args))(*args)

#updates the background and material colors based on current mode
def updateColors():
    glClearColor(*CLEAR_COLORS[mode]) #clear the screen

    frontColor = FRONT_COLORS[mode] if not blackAndWhite else FRONT_BW
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, vec(*frontColor))

    backColor = BACK_COLORS[mode] if not blackAndWhite else BACK_BW
    glMaterialfv(GL_BACK, GL_AMBIENT_AND_DIFFUSE, vec(*backColor))


#---parsing functions---#
def parseObj(string, batch):
    vertex_list = []
    face_list = []
    vertex_normals = {} #key is index of vertex, value is list of normals for three faces

    #bounding box for knot
    minCoord = [None, None, None]
    maxCoord = [None, None, None]

    for line in string.splitlines():
        data = [string.strip() for string in re.split(" +", line)]

        #assumes that vertices are written before faces
        if data[0] == 'v':
            thisVertex = [float(vertex) for vertex in data[1:]]

            for i in range(len(thisVertex)):
                if minCoord[i] == None or minCoord[i] > thisVertex[i]:
                    minCoord[i] = thisVertex[i]
                if maxCoord[i] == None or maxCoord[i] < thisVertex[i]:
                    maxCoord[i] = thisVertex[i]

            vertex_list += thisVertex

        if data[0] == 'f':
            indices = [int(tri) - 1 for tri in data[1:]]
            face_list += indices

            vertex1 = vertex_list[((indices[0]) * 3) : ((indices[0] + 1) * 3)]
            vertex2 = vertex_list[((indices[1]) * 3) : ((indices[1] + 1) * 3)]
            vertex3 = vertex_list[((indices[2]) * 3) : ((indices[2] + 1) * 3)]

            vector1 = createVector(vertex1, vertex2)
            vector2 = createVector(vertex1, vertex3)
            normal = crossProduct(vector1, vector2)

            for key in indices:
                if key in vertex_normals:
                    vertex_normals[key].append(normal)
                else:
                    vertex_normals[key] = [normal]

    #logic to resize the knot
    DESIRED_SIDE_LENGTH = 1
    center = [(max + min) / 2 for max, min in zip(maxCoord, minCoord)]

    sideLengths = [max - min for max, min in zip(maxCoord, minCoord)]
    divisor = max(sideLengths) / DESIRED_SIDE_LENGTH

    for index in range(len(vertex_list)):
        comp = index % 3 #0 for x, 1 for y, 2 for z
        vertex_list[index] -= center[comp]
        vertex_list[index] /= divisor

    calculatedVertexNormals = []
    for index, normals in sorted(vertex_normals.items()):
        sum = normals[0]
        for i in range(1, len(normals)):
            sum = vectorSum(sum, normals[i])

        calculatedVertexNormals += normalize(sum)

    batch.add_indexed(len(vertex_list)//3, GL_TRIANGLES, None, face_list, ('v3f', vertex_list), ('n3f', calculatedVertexNormals))

def writeToFile(string, name="knot.obj"):
    fileName = name
    outputFile = open(fileName, "w")
    outputFile.write(string)
    outputFile.close()

if __name__ == '__main__':
    #if called from the command line open obj file in argv[1] if present
    #otherwise read from standard in to get string
    if len(argv) > 1:
        renderObjFile(argv[1])
    else:
        renderObjString(stdin.read())
