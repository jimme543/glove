#!/usr/bin/python

import pygame
import smbus
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from math import radians
from pygame.locals import *
import time
import RPi.GPIO as io

SCREEN_SIZE = (800, 600)
SCALAR = .5
SCALAR2 = 0.2

io.setmode(io.BCM)
io.setwarnings(False)

# Set the constants for the pins for the motors
motor0fwd=4
motor0back=14

motor1fwd=15
motor1back=18

motor2fwd=17
motor2back=27

motor3fwd=23
motor3back=24

motor4fwd=25
motor4back=8

motor5fwd=5
motor5back=6

# need to use this because no longer running mpu vcc off 3.3V power rail
mpuVCC = 21
io.setup(mpuVCC, io.OUT)
io.output(mpuVCC, True)

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is etect command

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

##################################################################################
# these are the functions for reading from the mpu
##################################################################################
def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def getMPUvalues():
    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)

    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0

    #return str(get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))+" "+str(get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))
    return get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

##################################################################################
# These are all the functions i need to run the motors
#
# Set the motion of a single motor (forward, backward, stop)
################################################################################
def forward(motorNumFwd, motorNumBack):
    io.output(motorNumFwd, True)
    io.output(motorNumBack, False)

def backward(motorNumFwd, motorNumBack):
    io.output(motorNumFwd, False)
    io.output(motorNumBack, True)

def stop(motorNumFwd, motorNumBack):
    io.output(motorNumFwd, False)
    io.output(motorNumBack, False)

def stopAll():
    stop(motor0fwd, motor0back)
    stop(motor1fwd, motor0back)
    stop(motor2fwd, motor2back)
    stop(motor3fwd, motor3back)
    stop(motor4fwd, motor4back)
    stop(motor5fwd, motor5back)
    
##################################################################################
# This is the settings for the OpenGL stuff
##################################################################################
def resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / height, 0.1, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 1.0, -5.0,
              0.0, 1.0, 3.0,
              0.0, 1.0, 0.0)
    
def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_BLEND)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0));
        
###############################################################################
# This is the class that I will use to draw the parts of the hand (non finger)
###############################################################################
class Cuboid(object):

    def __init__(self, x, y, z, color):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.faces = 6
        self.handRotation = 1

    # Cuboid information
    normals = [ (0.0, 0.0, +1.0),  # front
                (0.0, 0.0, -1.0),  # back
                (+1.0, 0.0, 0.0),  # right
                (-1.0, 0.0, 0.0),  # left
                (0.0, +1.0, 0.0),  # top
                (0.0, -1.0, 0.0) ]  # bottom

    vertex_indices = [ (0, 1, 2, 3),  # front
                       (4, 5, 6, 7),  # back
                       (1, 5, 6, 2),  # right
                       (0, 4, 7, 3),  # left
                       (3, 2, 6, 7),  # top
                       (0, 1, 5, 4) ]  # bottom

    # each object has the ability to draw 
    def render(self):
        then = pygame.time.get_ticks()
        glColor(self.color)
        verticies = self.getVert()

        # Draw all 6 faces of the cube
        glBegin(GL_QUADS)

        # connecting the verticies, faces or the cuboid objects
        for face_no in xrange(self.faces):
            glNormal3dv(self.normals[face_no])
            v1, v2, v3, v4 = self.vertex_indices[face_no]
            glVertex(verticies[v1])
            glVertex(verticies[v2])
            glVertex(verticies[v3])
            glVertex(verticies[v4])
        glEnd()

    def getX(self):
        return self.x

    def setX(self, x):
        self.x = x

    def getY(self):
        return self.y

    def setY(self, y):
        self.y = y

    def getZ(self):
        return self.z

    def setZ(self, z):
        self.z = z

    def getHeight(self): # y axis?
        if self.getHandRotation() == 0:
            return 2.0
        else:
            return .1

    def getWidth(self): # x axis?
        if self.getHandRotation() == 0:
            return .1
        else:
            return 2.0
    
    def getDepth(self): # z axis?
        return 1.0

    def getHandRotation(self):
        return self.handRotation

    def setHandRotation(self, num):
        self.handRotation = num

    def getVert(self):
        if self.handRotation == 1:
            return self.setHorizontal()
        elif self. handRotation == 0:
            return self.setVertical()
        else: # handRotation == -1
            return self.setHorizontal()

    def setHorizontal(self):
        x = self.getX()
        y = self.getY()
        z = self.getZ()
        vert = [(x-1.0, y-0.05, z+0.5),
                (x+1.0, y-0.05, z+0.5),
                (x+1.0, y+0.05, z+0.5),
                (x-1.0, y+0.05, z+0.5),
                (x-1.0, y-0.05, z-0.5),
                (x+1.0, y-0.05, z-0.5),
                (x+1.0, y+0.05, z-0.5),
                (x-1.0, y+0.05, z-0.5) ]
        return vert
    
    def setVertical(self):
        x = self.getX()
        y = self.getY()
        z = self.getZ()
        vert = [(x-0.05, y-1.0, z+0.5),
                (x+0.05, y-1.0, z+0.5),
                (x+0.05, y+1.0, z+0.5),
                (x-0.05, y+1.0, z+0.5),
                (x-0.05, y-1.0, z-0.5),
                (x+0.05, y-1.0, z-0.5),
                (x+0.05, y+1.0, z-0.5),
                (x-0.05, y+1.0, z-0.5) ]
        return vert
        
###############################################################################
# This is the class that I will use to draw the fingers
###############################################################################
class Finger(object):

    def __init__(self, x, y, z, color):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.faces = 6
        self.handRotation = 1
    
    # Finger information
    normals = [ (0.0, 0.0, +1.0),  # front
                (0.0, 0.0, -1.0),  # back
                (+1.0, 0.0, 0.0),  # right
                (-1.0, 0.0, 0.0),  # left
                (0.0, +1.0, 0.0),  # top
                (0.0, -1.0, 0.0) ]  # bottom

    vertex_indices = [ (0, 1, 2, 3),  # front
                       (4, 5, 6, 7),  # back
                       (1, 5, 6, 2),  # right
                       (0, 4, 7, 3),  # left
                       (3, 2, 6, 7),  # top
                       (0, 1, 5, 4) ]  # bottom

    def render(self):
        then = pygame.time.get_ticks()
        glColor(self.color)
        verticies = self.getVert()

        # Draw all 6 faces of the cube
        glBegin(GL_QUADS)

        for face_no in xrange(self.faces):
            glNormal3dv(self.normals[face_no])
            v1, v2, v3, v4 = self.vertex_indices[face_no]
            glVertex(verticies[v1])
            glVertex(verticies[v2])
            glVertex(verticies[v3])
            glVertex(verticies[v4])
        glEnd()

    # getters and setters
    def getX(self):
        return self.x

    def setX(self, x):
        self.x = x

    def getY(self):
        return self.y

    def setY(self, y):
        self.y = y

    def getZ(self):
        return self.z

    def setZ(self, z):
        self.z = z

    def getHeight(self): # y axis?
        if self.getHandRotation() == 0:
            return .5
        else:
            return .1         

    def getWidth(self): # x axis?
        if self.getHandRotation() == 0:
            return .1
        else:
            return .5
    
    def getDepth(self): # z axis?
        return .5

    def getHandRotation(self):
        return self.handRotation

    def setHandRotation(self, num):
        self.handRotation = num

    def getVert(self):
        if self.handRotation == 1:
            return self.setHorizontal()
        elif self. handRotation == 0:
            return self.setVertical()
        else: # handRotation == -1
            return self.setHorizontal()

    def setHorizontal(self):
        x = self.getX()
        y = self.getY()
        z = self.getZ()
        vert = [(x-0.25, y-0.05, z+0.25),
                (x+0.25, y-0.05, z+0.25),
                (x+0.25, y+0.05, z+0.25),
                (x-0.25, y+0.05, z+0.25),
                (x-0.25, y-0.05, z-0.25),
                (x+0.25, y-0.05, z-0.25),
                (x+0.25, y+0.05, z-0.25),
                (x-0.25, y+0.05, z-0.25) ]
        return vert

    def setVertical(self):
        x = self.getX()
        y = self.getY()
        z = self.getZ()
        vert = [(x-0.05, y-0.25, z+0.25),
                (x+0.05, y-0.25, z+0.25),
                (x+0.05, y+0.25, z+0.25),
                (x-0.05, y+0.25, z+0.25),
                (x-0.05, y-0.25, z-0.25),
                (x+0.05, y-0.25, z-0.25),
                (x+0.05, y+0.25, z-0.25),
                (x-0.05, y+0.25, z-0.25)  ]
        return vert

###############################################################################
# This is the class that I will use to draw the parts of the hand (non finger)
###############################################################################
class Thingy(object):

    def __init__(self, x, y, z, color):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.faces = 6

    # Cuboid information
    normals = [ (0.0, 0.0, +1.0),  # front
                (0.0, 0.0, -1.0),  # back
                (+1.0, 0.0, 0.0),  # right
                (-1.0, 0.0, 0.0),  # left
                (0.0, +1.0, 0.0),  # top
                (0.0, -1.0, 0.0) ]  # bottom

    vertex_indices = [ (0, 1, 2, 3),  # front
                       (4, 5, 6, 7),  # back
                       (1, 5, 6, 2),  # right
                       (0, 4, 7, 3),  # left
                       (3, 2, 6, 7),  # top
                       (0, 1, 5, 4) ]  # bottom

    # each object has the ability to draw 
    def render(self):
        then = pygame.time.get_ticks()
        glColor(self.color)
        verticies = self.getVert()

        # Draw all 6 faces of the cube
        glBegin(GL_QUADS)

        # connecting the verticies, faces or the cuboid objects
        for face_no in xrange(self.faces):
            glNormal3dv(self.normals[face_no])
            v1, v2, v3, v4 = self.vertex_indices[face_no]
            glVertex(verticies[v1])
            glVertex(verticies[v2])
            glVertex(verticies[v3])
            glVertex(verticies[v4])
        glEnd()

    def getX(self):
        return self.x

    def setX(self, x):
        self.x = x

    def getY(self):
        return self.y

    def setY(self, y):
        self.y = y

    def getZ(self):
        return self.z

    def setZ(self, z):
        self.z = z

    def getHeight(self):
        return .1

    def getWidth(self): 
        return .1
    
    def getDepth(self): 
        return .1

    def getVert(self):
        x = self.getX()
        y = self.getY()
        z = self.getZ()
        vert = [(x-0.05, y-0.05, z+0.05),
                (x+0.05, y-0.05, z+0.05),
                (x+0.05, y+0.05, z+0.05),
                (x-0.05, y+0.05, z+0.05),
                (x-0.05, y-0.05, z-0.05),
                (x+0.05, y-0.05, z-0.05),
                (x+0.05, y+0.05, z-0.05),
                (x-0.05, y+0.05, z-0.05) ]
        return vert
        
###############################################################################
# change the orientation of the hand depending on where the MPU is
# loop through all pieces of the hand and place them in the right place
#
# places each piece relative to where the ball of tha hand's midpoint is at
###############################################################################
def setHandPosition(num ,obj0, obj1, obj2, obj3, obj4, obj5):
                 # (num, ball, palm, pointer, middle, ring, thumb)

    x = obj0.getX()
    y = obj0.getY()
    z = obj0.getZ()
    
    # the hand is palm down
    if num == 1: 
        obj0.setHandRotation(1) # ball
        obj0.setX(x)
        obj0.setY(y)
        obj0.setZ(z)
        
        obj1.setHandRotation(1) # palm
        obj1.setX(x)
        obj1.setY(y)
        obj1.setZ(z+1.25)
        
        obj2.setHandRotation(1) # pointer
        obj2.setX(x-0.80)
        obj2.setY(y)
        obj2.setZ(z+3.5)
        
        obj3.setHandRotation(1) # middle
        obj3.setX(x-0.20)
        obj3.setY(y)
        obj3.setZ(z+3.75)
        
        obj4.setHandRotation(1) # ring
        obj4.setX(x+0.40)
        obj4.setY(y)
        obj4.setZ(z+3.5)
        
        obj5.setHandRotation(1) # thumb
        obj5.setX(x-2.5)
        obj5.setY(y)
        obj5.setZ(z+1.0)

    # the hand is vertical
    elif num == 0: 
        obj0.setHandRotation(0) # ball
        obj0.setX(x)
        obj0.setY(y)
        obj0.setZ(z)
        
        obj1.setHandRotation(0) # palm
        obj1.setX(x)
        obj1.setY(y)
        obj1.setZ(z+1.25)
        
        obj2.setHandRotation(0) # pointer
        obj2.setX(x)
        obj2.setY(y-0.80)
        obj2.setZ(z+3.5)
        
        obj3.setHandRotation(0) # middle
        obj3.setX(x)
        obj3.setY(y-0.20)
        obj3.setZ(z+3.75)
        
        obj4.setHandRotation(0) # ring
        obj4.setX(x)
        obj4.setY(y+0.40)
        obj4.setZ(z+3.5)
        
        obj5.setHandRotation(0) # thumb
        obj5.setX(x)
        obj5.setY(y+2.5)
        obj5.setZ(z+1.0)

    # the hand is palm up
    elif num == -1: 
        obj0.setHandRotation(-1) # ball
        obj0.setX(x)
        obj0.setY(y)
        obj0.setZ(z)
        
        obj1.setHandRotation(-1) # palm
        obj1.setX(x)
        obj1.setY(y)
        obj1.setZ(z+1.25)
        
        obj2.setHandRotation(-1) # pointer
        obj2.setX(x+0.80)
        obj2.setY(y)
        obj2.setZ(z+3.5)
        
        obj3.setHandRotation(-1) # middle
        obj3.setX(x+0.20)
        obj3.setY(y)
        obj3.setZ(z+3.75)
        
        obj4.setHandRotation(-1) # ring
        obj4.setX(x-0.40)
        obj4.setY(y)
        obj4.setZ(z+3.5)
        
        obj5.setHandRotation(-1) # thumb
        obj5.setX(x+2.5)
        obj5.setY(y)
        obj5.setZ(z+1.0)

###############################################################################
# Pass in two objects and do collision detection 
###############################################################################
def collide(obj1, obj2):
    x1 = obj1.getX()
    x2 = obj2.getX()
    y1 = obj1.getY()
    y2 = obj2.getY()
    z1 = obj1.getZ()
    z2 = obj2.getZ()

    w1 = obj1.getWidth()/2
    w2 = obj2.getWidth()/2
    h1 = obj1.getHeight()/2
    h2 = obj2.getHeight()/2
    d1 = obj1.getDepth()/2
    d2 = obj2.getDepth()/2

    # collision detection like a boss!!! thank you cs people!!!!
    if (    x1-w1 <= x2+w2 and x1-w1 >= x2-w2
        and y1-h1 <= y2+h2 and y1-h1 >= y2-h2
        and z1-d1 <= z2+d2 and z1-d1 >= z2-d2):
        print "Collision #1"
        return True
    
    if (    x1+w1 >= x2-w2 and x1+w1 <= x2+w2
        and y1+h1 >= y2-h2 and y1+h1 <= y2+h2
        and z1+d1 >= z2-d2 and z1+d1 <= z2+d2):
        print "Collision #2"
        return True
    return False
    

###############################################################################
# This is the "main" function for the program
###############################################################################
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF)
resize(*SCREEN_SIZE)
init()
clock = pygame.time.Clock()

# Define the pins as output pins
io.setup(motor0fwd, io.OUT)
io.setup(motor0back, io.OUT)

io.setup(motor1fwd, io.OUT)
io.setup(motor1back, io.OUT)

io.setup(motor2fwd, io.OUT)
io.setup(motor2back, io.OUT)

io.setup(motor3fwd, io.OUT)
io.setup(motor3back, io.OUT)

io.setup(motor4fwd, io.OUT)
io.setup(motor4back, io.OUT)

io.setup(motor5fwd, io.OUT)
io.setup(motor5back, io.OUT)

stopAll()

# Create objects of the hand 
ball = Cuboid(0.0, 0.0, 0.0, (.5, .5, .7)) # first three are position
palm = Cuboid(0.0, 0.0, 1.25, (.5, .5, .1)) # parentheses is color

pointer = Finger(-0.80, 0.0, 3.5, (.3, .3, .3))
middle = Finger(-0.20, 0.0, 3.75, (.3, .3, .3))
ring = Finger(0.4, 0.0, 3.5, (.3, .3, .3))
thumb = Finger(-2.5, 0.0, 1.0, (.3, .3, .3))

# this is the object that will be touched
obj = Thingy(0,1,0, (.4,.4,.4))

collisionObjects = [ ball, palm, pointer, middle, ring, thumb ]

lastCheck = 0

# the MAIN LOOP of the program
while True:
    then = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == QUIT:
            stopAll() # make sure to turn off motors when quitting
            exit(0)
        if event.type == KEYUP and event.key == K_ESCAPE:
            stopAll() # make sure to turn off motors when quitting
            exit(0)
        if event.type == KEYDOWN and event.key== K_DOWN: # testing only
            obj.setY(obj.getY()-.1)
        if event.type == KEYDOWN and event.key== K_UP:  # testing only
            obj.setY(obj.getY()+.1)
        if event.type == KEYDOWN and event.key== K_LEFT:  # testing only
            obj.setX(obj.getX()+.1)
        if event.type == KEYDOWN and event.key== K_RIGHT:  # testing only
            obj.setX(obj.getX()-.1)
        if event.type == KEYDOWN and event.key== K_1:  # testing only
            obj.setZ(obj.getZ()-.1)
        if event.type == KEYDOWN and event.key== K_2:  # testing only
            obj.setZ(obj.getZ()+.1)
            
    # this is where the value from the MPU get inputted
    values = getMPUvalues()
    y_angle = values

    # this is where i do the rotating on the entire hand
    # the mpu would have to be placed at the inside of the wrist
    # with the pins on top of the arm for this to work
    if y_angle > 45.0: # this means that the hand is palm down
        if lastCheck == 1:
            pass # this is a do nothing command
        else:
            setHandPosition(1, ball, palm, pointer, middle, ring, thumb)
            lastcheck = 1
    elif y_angle > -45.0: # this means that the hand it vertical
        if lastCheck == 0:
            pass
        else:
            setHandPosition(0, ball, palm, pointer, middle, ring, thumb)
            lastCheck = 0
    else: # this means that the hand is palm up
        if lastCheck == -1:
            pass
        else:
            setHandPosition(-1, ball, palm, pointer, middle, ring, thumb)
            lastCheck = -1
        
    #print "y ang: ", y_angle

    # RIGHT HERE is where I will do the POSITION change of the whole hand
    # in the x, y, z space

    # this is where all the drawing is done for the objects
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    #glRotate(float(x_angle), -1, 0, 0) # im taking this out
    #glRotate(-float(y_angle), 0, 0, -1) # this too :)
        
    ball.render()
    palm.render()
    pointer.render()
    middle.render()
    ring.render()
    thumb.render()
    
    obj.render()
      
    glPopMatrix()
    pygame.display.flip()

    
    # do collisition detection here
    motorMatrix = [False, False, False, False, False, False]
    i = 0
    for something in collisionObjects:
        if collide(obj, something):
            motorMatrix[i] = True # set appropriate place in matrix to true
        i += 1
        
    # control the motors here
    if motorMatrix[0]:
        forward(motor0fwd, motor0back) # 3 motor ball
        print "ball ON"
    else:
        stop(motor0fwd, motor0back)
        print "ball OFF"
    if motorMatrix[1]:                  # 2 motors palm
        forward(motor1fwd, motor1back)
        print "palm ON"
    else:
        stop(motor1fwd, motor1back)
        print "palm OFF"
    if motorMatrix[2]:                  #1 motor pointer
        forward(motor3fwd, motor3back)
        print "pointer ON"
    else:
        stop(motor3fwd, motor3back)
        print "pointer OFF"
    if motorMatrix[3]:                  # 1 motor middle
        forward(motor4fwd, motor4back)
        print "middle ON"
    else:
        stop(motor4fwd, motor4back)
        print "middle OFF"
    if motorMatrix[4]:                  # 2 motors ring
        forward(motor2fwd, motor2back)
        print "ring ON"
    else:
        stop(motor2fwd, motor2back)
        print "ring OFF"
    if motorMatrix[5]:                  # 1 motor thumb
        forward(motor5fwd, motor5back)
        print "thumb ON"
    else:
        stop(motor5fwd, motor5back)
        print "thumb OFF"

    print 
stopAll()

