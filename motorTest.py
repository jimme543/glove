#!/usr/bin/python
import math
import time
import RPi.GPIO as io
#from rrb3 import *

io.setmode(io.BCM)
io.setwarnings(False)

# Set the constants for the pins
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

def stopAll():
    stop(motor0fwd, motor0back)
    stop(motor1fwd, motor0back)
    stop(motor2fwd, motor2back)
    stop(motor3fwd, motor3back)
    stop(motor4fwd, motor4back)
    stop(motor5fwd, motor5back)

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

#MAIN FUNCTION
stopAll()

forward(motor0fwd, motor0back) # 3 motors - ball
forward(motor1fwd, motor1back) # 2 motors - palm
forward(motor2fwd, motor2back) # 2 motors - ring
forward(motor3fwd, motor3back) # 1 motor - pointer
forward(motor4fwd, motor4back) # 1 motor - middle
forward(motor5fwd, motor5back) # 1 motor - thumb
time.sleep(1)

stopAll()

