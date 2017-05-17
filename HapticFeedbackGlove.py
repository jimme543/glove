#!/usr/bin/python

##################################################################
# # Written and put together by none other than
#
#
#               JAMES CRIDDLE
#
#
# for funzies/ECEN 461 (Adv. Embedded Systems) project
#
# The point of this project was to get a Haptic Feedback Glove
# working with the Raspberry Pi. I use 3D to show objects and
# do collision detection to tell when to turn on and off the
# motors on the glove.
#
# HARDWARE:
# Raspberry pi 2 or higher
# mpu 6050 (I got mine on amazon for about 4 dollars)
# Wii remote
# Bluetooth dongle
# reflecting tape
# L293D Motor Drivers x3
# 10 small vibrating motors, ~3.3V 80mA
# infrared LED x4
# a resistor (I used a ~500 Ohm)
# battery
# mouse and keyboard
# monitor
#
# SOFTWARE
# (installation instructions for all libraries used here)
# sudo apt-get update
# sudo apt-get upgrade
# reboot
# 
# for the mpu650:
# sudo apt-get install python-smbus
# and go to raspi-config and enable I2C
#
# forthe OpenGl and pygame:
# sudo apt-get install python-opengl
# sudo apt-get install python-pygame
#
# for the wiimote and cwiid:
# sudo apt-get install bluetooth
# sudo service bluetooth status
# /etc/init.d/bluetooth start
# hcitool dev
# hcitool scan
# sudo apt-get install python-cwiid
#
# Things I still need to add:
# Flex sensors to detect when a finger is bent
# Some kind of sensor to detect the position of the hand in the z direction
# Kalman Filter to get rid of noise from the MPU
# a pcb board to put all the components onto
#
#
# Things I think I will do..
# make an object movable with the hand pushing it
##################################################################

import pygame
import smbus
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from math import radians
from pygame.locals import *
import time
import RPi.GPIO as io
import cwiid
import sys

SCREEN_SIZE = (800, 600)
#wiimote camera (1024, 768) 
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

##################################################################
# these are the functions for reading from the mpu
#
# If I want to make this more stable I could run a Kalman Filter
##################################################################
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

###################################################################
# These are all the functions i need to run the motors
#
# Set the motion of a single motor (forward, backward, stop)
###################################################################
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
    
#################################################################
# This is the settings for the OpenGL stuff
#################################################################
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
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
    
################################################################
# This is the class that I will use to draw the fingers
################################################################
class Cuboid(object):

    def __init__(self, x, y, z, color, width, height, depth):
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.faces = 6
        self.handRotation = 1
        self.width = width
        self.height = height
        self.depth = depth
        self.bounce = 0
        self.vx = 0
        self.vy = 0
    
    # Cube information
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

    def getHeight(self): # y axis
        if self.getHandRotation() == 0:
            return self.width
        else:
            return self.height

    def getWidth(self): # x axis
        if self.getHandRotation() == 0:
            return self.height
        else:
            return self.width
    
    def getDepth(self): # z axis
        return self.depth

    def getHandRotation(self):
        return self.handRotation

    def setHandRotation(self, num):
        self.handRotation = num

    def getBounce(self):
        return self.bounce

    def setBounce(self, thing):
        self.bounce = thing

    def getVX(self):
        return self.vx

    def setVX(self, vx):
        self.vx = vx

    def getVY(self):
        return self.vy

    def setVY(self, vy):
        self.vy = vy

    def getVert(self):
        if self.handRotation == 1: # palm down
            return self.setHorizontal()
        elif self. handRotation == 0: # hand vertical
            return self.setVertical()
        else: # handRotation == -1  # palm up
            return self.setHorizontal()

    def setHorizontal(self):
        x = self.getX()
        y = self.getY()
        z = self.getZ()
        w = self.getWidth()/2.0
        h = self.getHeight()/2.0
        d = self.getDepth()/2.0
        vert = [(x-w, y-h, z+d),
                (x+w, y-h, z+d),
                (x+w, y+h, z+d),
                (x-w, y+h, z+d),
                (x-w, y-h, z-d),
                (x+w, y-h, z-d),
                (x+w, y+h, z-d),
                (x-w, y+h, z-d) ]
        return vert

    def setVertical(self):
        x = self.getX()
        y = self.getY()
        z = self.getZ()
        w = self.getWidth()/2.0
        h = self.getHeight()/2.0
        d = self.getDepth()/2.0
        vert = [(x-w, y-h, z+d),
                (x+w, y-h, z+d),
                (x+w, y+h, z+d),
                (x-w, y+h, z+d),
                (x-w, y-h, z-d),
                (x+w, y-h, z-d),
                (x+w, y+h, z-d),
                (x-w, y+h, z-d) ]
        return vert

    def bounceObject(self):
        if not self.getBounce():
            return            
        elif self.getBounce() == 1:
            if self.getY() <= 3:
                self.setY(self.getY()+.2)
            else:
                self.setBounce(-1)
        else:
            if self.getY() > 0:
                self.setY(self.getY()-.2)
            else:
                self.setBounce(0)
                
################################################################
# change the orientation of the hand depending on where the MPU is
# loop through all pieces of the hand and place them in the right place
#
# places each piece relative to where the ball of tha hand's midpoint is at
################################################################
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
        obj2.setY(y+0.4)
        obj2.setZ(z+3.5)
        
        obj3.setHandRotation(0) # middle
        obj3.setX(x)
        obj3.setY(y-0.20)
        obj3.setZ(z+3.75)
        
        obj4.setHandRotation(0) # ring
        obj4.setX(x)
        obj4.setY(y-0.8)
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

    # if I have time use the x axis on the mpu to do
    # extra rotations on the hand

################################################################
# Wiimote function to get the IR points
################################################################
def callback(mesg_list, time):
        global ballPosX
        global ballPosY
        L1 = []
	for mesg in mesg_list:
            if mesg[0] == cwiid.MESG_IR:
		valid_src = False
		for src in mesg[1]:
		    if src:
			valid_src = True
			L1.append( src['pos']) 
        if L1:
            x = 0
            y = 0
            i = 0
            for thing in L1:
                x += L1[i][0]
                y += L1[i][1]
                i += 1
                
            x = x/i
            y = y/i
            x = 1024 - x
            y = 768 - y
            #print "x: ", x, " y: ", y
            #print "bX: ", ballPosX, " bY: ", ballPosY
            #wiimote camera (1024, 768)

            ballPosX = .00488*x
            ballPosY = .00651*y

################################################################
# Pass in two objects and do collision detection 
################################################################
def collide(obj1, obj2):
    x1 = obj1.getX()
    x2 = obj2.getX()
    y1 = obj1.getY()
    y2 = obj2.getY()
    z1 = obj1.getZ()
    z2 = obj2.getZ()

    w1 = obj1.getWidth()/2.0
    w2 = obj2.getWidth()/2.0
    h1 = obj1.getHeight()/2.0
    h2 = obj2.getHeight()/2.0
    d1 = obj1.getDepth()/2.0
    d2 = obj2.getDepth()/2.0
    
    # AXIS ALIGNED BOUNDING BOX collision
    if (    x1-w1 <= x2+w2 and x1+w1 >= x2-w2
        and y1-h1 <= y2+h2 and y1+h1 >= y2-h2
        and z1-d1 <= z2+d2 and z1+d1 >= z2-d2):
        #print "Collision"
        return True
        
    return False

################################################################
# Pass in two objects and do collision detection 
################################################################
def moveObject(movingObj, obj1):
    if obj1.getHandRotation()==1:
        if obj1.getY()<movingObj.getY():
            movingObj.setY(movingObj.getY()-.15)
    elif obj1.getHandRotation()==0:
        if obj1.getX()<movingObj.getX():
            movingObj.setX(movingObj.getX()+.15)
        elif obj1.getX()>movingObj.getX():
            movingObj.setX(movingObj.getX()-.15)
    elif obj1.getHandRotation()==-1:
        if obj1.getY()<movingObj.getY():
            movingObj.setY(movingObj.getY()+.15)


################################################################
# This is the "main" function for the program
################################################################
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
ball = Cuboid(0.0, 0.0, 0.0,  (.5, .5, .7), 2.0, 0.1, 1.0)  # all these numbers
palm = Cuboid(0.0, 0.0, 1.25, (.5, .5, .1), 2.0, 0.1, 1.0)  # need to be floats

pointer = Cuboid(-0.80, 0.0, 3.5,  (.3, .3, .3), 0.5, 0.1, 0.5)
middle  = Cuboid(-0.20, 0.0, 3.75, (.3, .3, .3), 0.5, 0.1, 0.5)
ring    = Cuboid(0.4,   0.0, 3.5,  (.3, .3, .3), 0.5, 0.1, 0.5)
thumb   = Cuboid(-2.5,  0.0, 1.0,  (.3, .3, .3), 0.5, 0.1, 0.5)

# this is the object that will be touched
obj = Cuboid(0.0, 1.0, 0.0, (.4, .4, .4), .50, .100, .50)

collisionObjects = [ palm, ball, pointer, middle, ring, thumb ]

lastCheck = 0

rpt_mode = 0
mesg = False

global ballPosX 
global ballPosY

ballPosX = ball.getX()
ballPosY = ball.getY()

setHandPosition(-1, ball, palm, pointer, middle, ring, thumb)

#Connect to address given on command-line, if present
print 'Put Wiimote in discoverable mode now (press 1+2)...'
global wiimote
if len(sys.argv) > 1:
    wiimote = cwiid.Wiimote(sys.argv[1])
else:
    wiimote = cwiid.Wiimote()

wiimote.mesg_callback = callback

wiimote.enable(cwiid.FLAG_MESG_IFC);
rpt_mode = cwiid.RPT_IR
wiimote.rpt_mode = rpt_mode

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
            
    # value from the MPU is inputted
    values = getMPUvalues()
    y_angle = values

    # rotating of the entire hand
    # the mpu has to be placed at the inside of the wrist
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

    # moving of the hand in the x direction
    if ballPosX == ball.getX():
        pass
    else:
        changeX = ballPosX + ball.getX() - 2.5
        ball.setX(ball.getX()-changeX)
        palm.setX(palm.getX()-changeX)
        pointer.setX(pointer.getX()-changeX)
        middle.setX(middle.getX()-changeX)
        ring.setX(ring.getX()-changeX)
        thumb.setX(thumb.getX()-changeX)
        ballPosX = ball.getX()

    # moving of the hand in the y direction
    if ballPosY == ball.getY():
        pass
    else:
        changeY = ballPosY + ball.getY() - 3.0
        ball.setY(ball.getY()-changeY)
        palm.setY(palm.getY()-changeY)
        pointer.setY(pointer.getY()-changeY)
        middle.setY(middle.getY()-changeY)
        ring.setY(ring.getY()-changeY)
        thumb.setY(thumb.getY()-changeY)
        ballPosY = ball.getY()

    # drawing for all the objects
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
        
    ball.render()
    palm.render()
    pointer.render()
    middle.render()
    ring.render()
    thumb.render()
    
    obj.render()
      
    glPopMatrix()
    pygame.display.flip()

    
    # collision detection 
    motorMatrix = [False, False, False, False, False, False]
    i = 0
    for something in collisionObjects:
        if collide(obj, something):
            motorMatrix[i] = True # set appropriate place in matrix to true
            #obj.setBounce(1)
            #moveObject(obj, ball)
        i += 1

    #obj.bounceObject() # this is just for fun, take out for no object moving
    
    # control the motors 
    if motorMatrix[1]:                  # 2 motors palm
        forward(motor1fwd, motor1back)
        #print "palm ON", "-- ", motorMatrix[1]
    else:
        stop(motor1fwd, motor1back)
        #print "palm OFF", "-- ", motorMatrix[1]
    if motorMatrix[0]:                  # 3 motor ball
        forward(motor0fwd, motor0back) 
        #print "ball ON", "-- ", motorMatrix[0]
    else:
        stop(motor0fwd, motor0back)
        #print "ball OFF", "-- ", motorMatrix[0]
    if motorMatrix[2]:                  #1 motor pointer
        forward(motor3fwd, motor3back)
        #print "pointer ON", "-- ", motorMatrix[2]
    else:
        stop(motor3fwd, motor3back)
        #print "pointer OFF", "-- ", motorMatrix[2]
    if motorMatrix[3]:                  # 1 motor middle
        forward(motor4fwd, motor4back)
        #print "middle ON", "-- ", motorMatrix[3]
    else:
        stop(motor4fwd, motor4back)
        #print "middle OFF", "-- ", motorMatrix[3]
    if motorMatrix[4]:                  # 2 motors ring
        forward(motor2fwd, motor2back)
        #print "ring ON", "-- ", motorMatrix[4]
    else:
        stop(motor2fwd, motor2back)
        #print "ring OFF", "-- ", motorMatrix[4]
    if motorMatrix[5]:                  # 1 motor thumb
        forward(motor5fwd, motor5back)
        #print "thumb ON", "-- ", motorMatrix[5]
    else:
        stop(motor5fwd, motor5back)
        #print "thumb OFF", "-- ", motorMatrix[5]

    #print
    
stopAll()
wiimote.close()
