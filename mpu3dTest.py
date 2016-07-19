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

    return str(get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))+" "+str(get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))

##################################################################################
# This is the settings for the OpenGL stuff
##################################################################################
def resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / height, 0.001, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 1.0, -5.0,
              0.0, 0.0, 0.0,
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
class Cube(object):

    def __init__(self, position, color):
        self.position = position  # the position is the centroid of the cube
        self.color = color
        self.faces = 6
        self.vert = [(self.position[0]-1.0, self.position[1]-0.05, self.position[2]+0.5),
                     (self.position[0]+1.0, self.position[1]-0.05, self.position[2]+0.5),
                     (self.position[0]+1.0, self.position[1]+0.05, self.position[2]+0.5),
                     (self.position[0]-1.0, self.position[1]+0.05, self.position[2]+0.5),
                     (self.position[0]-1.0, self.position[1]-0.05, self.position[2]-0.5),
                     (self.position[0]+1.0, self.position[1]-0.05, self.position[2]-0.5),
                     (self.position[0]+1.0, self.position[1]+0.05, self.position[2]-0.5),
                     (self.position[0]-1.0, self.position[1]+0.05, self.position[2]-0.5) ]
    
    # Cube information
    num_faces = 6

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
        verticies = self.vert

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
        
###############################################################################
# This is the class that I will use to draw the fingers
###############################################################################
class Finger(object):

    def __init__(self, position, color):
        self.__position = position  # the position is the centroid of the cube
        self.color = color
        self.faces = 6

        self.vert = [(self.position[0]-0.25, self.position[1]-0.05, self.position[2]+0.25),
                     (self.position[0]+0.25, self.position[1]-0.05, self.position[2]+0.25),
                     (self.position[0]+0.25, self.position[1]+0.05, self.position[2]+0.25),
                     (self.position[0]-0.25, self.position[1]+0.05, self.position[2]+0.25),
                     (self.position[0]-0.25, self.position[1]-0.05, self.position[2]-0.25),
                     (self.position[0]+0.25, self.position[1]-0.05, self.position[2]-0.25),
                     (self.position[0]+0.25, self.position[1]+0.05, self.position[2]-0.25),
                     (self.position[0]-0.25, self.position[1]+0.05, self.position[2]-0.25) ]
    
    # Cube information
    num_faces = 6

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
        vertices = self.vert

        # Draw all 6 faces of the cube
        glBegin(GL_QUADS)

        for face_no in xrange(self.faces):
            glNormal3dv(self.normals[face_no])
            v1, v2, v3, v4 = self.vertex_indices[face_no]
            glVertex(vertices[v1])
            glVertex(vertices[v2])
            glVertex(vertices[v3])
            glVertex(vertices[v4])
        glEnd()

    def getX(self):
        return self.__position[0]

    def setX(self, x):
        self.__position[0] = x

###############################################################################
# This is the where I will do the collision detection
#
# This is a temporary way to test, not permanent
# need to add in the velocity the object it moving and if it reaches an
# invisible boundary around the area then it will tigger true
###############################################################################
def collide(obj1, obj2):
    if obj1.position[0] == obj2.position[0]:
        if obj1.position[1] == obj2.position[1]:
            if obj1.position[2] == obj2.position[2]:
                print "COLLISION!!!"
                return True
    return False

###############################################################################
# This is the "main" function for the program
#if __name__ == "__main__":
###############################################################################
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF)
resize(*SCREEN_SIZE)
init()
clock = pygame.time.Clock()
    
ball = Cube((0.0, 0.0, 0.0), (.5, .5, .7)) # first parentheses is position
palm = Cube((0.0, 0.0, 1.25), (.5, .5, .1)) # second parentheses is color
pointer = Finger((-0.80, 0.0, 3.5), (.3, .3, .3))
middle = Finger((-0.20, 0.0, 3.75), (.3, .3, .3))
ring = Finger((0.4, 0.0, 3.5), (.3, .3, .3))
thumb = Finger((-2.5, 0.0, 1.0), (.3, .3, .3))
obj = Finger((1,1,1), (.4,.4,.4))
    
angle = 0 # this isnt used...not sure why it is in here...but ill keep it 

# Here is the bulk of where the code will spend its time
while True:
    then = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == QUIT:
            exit(0)
        if event.type == KEYUP and event.key == K_ESCAPE:
            exit(0)
        if event.type == KEYUP and event.key== K_RIGHT:
            setattr(obj, obj.position[0], obj.position[0]+.1)
            
    # this is where the value from the MPU get inputted
    values = getMPUvalues()
    num = values.split(' ')
    x_angle = num[0]
    y_angle = num[1]
        
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    glRotate(float(x_angle), -1, 0, 0) #these last numbers change orientation
    glRotate(-float(y_angle), 0, 0, -1) # when tilted a certain direction
        
    ball.render()
    palm.render()
    pointer.render()
    middle.render()
    ring.render()
    thumb.render()
    obj.render()
        
    glPopMatrix()
    pygame.display.flip()

    obj.getX()
    # do collisition detection here


