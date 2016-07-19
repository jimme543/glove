#!/usr/bin/python
import math
import time
import RPi.GPIO as io
#from rrb3 import *

io.setmode(io.BCM)
io.setwarnings(False)

# Set the constants for the pins
motor0fwd=27
motor0back=22

motor1fwd=20
motor1back=21

#motor2fwd=
#motor2back=

#motor3fwd=
#motor3back=

#motor4fwd=
#motor4back=

#motor5fwd=
#motor5back=

#motor6fwd=
#motor6back=

#motor7fwd=
#motor7back=

#motor8fwd=
#motor8back=

#motor9fwd=
#motor9back=

# Set the motion of a single motor (forward, backward, stop)
def forward(motorNumFwd, motorNumBack):
    io.output(motorNumFwd, True)
    io.output(motorNumBack, False)

def backward(motorNumFwd, motorNumBack):
    io.output(motorNumFwd, False)
    io.output(motorNumBack, True)

def stop(motorNumFwd, motorNumBack):
    io.output(motorNumFwd, False)
    io.output(motorNumBack, False)

# Define the pins as output pins
io.setup(motor0fwd, io.OUT)
io.setup(motor0back, io.OUT)
io.setup(motor1fwd, io.OUT)
io.setup(motor1back, io.OUT)
#io.setup(motor2fwd, io.OUT)
#io.setup(motor2back, io.OUT)
#io.setup(motor3fwd, io.OUT)
#io.setup(motor3back, io.OUT)
#io.setup(motor4fwd, io.OUT)
#io.setup(motor4back, io.OUT)
#io.setup(motor5fwd, io.OUT)
#io.setup(motor5back, io.OUT)
#io.setup(motor6fwd, io.OUT)
#io.setup(motor6back, io.OUT)
#io.setup(motor7fwd, io.OUT)
#io.setup(motor7back, io.OUT)
#io.setup(motor8fwd, io.OUT)
#io.setup(motor8back, io.OUT)
#io.setup(motor9fwd, io.OUT)
#io.setup(motor9back, io.OUT)

#MAIN FUNCTION

forward(motor0fwd, motor0back)
#forward(motor1fwd, motor1back)
time.sleep(1)
backward(motor0fwd, motor0back)
time.sleep(1)
stop(motor0fwd, motor0back)
#stop(motor1fwd, motor1back)


