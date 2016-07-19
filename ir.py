#!/usr/bin/python
import pygame
from pygame.locals import *
import cwiid
import sys
from OpenGL.GL import *
from OpenGL.GLU import *


SCREEN_SIZE = (800, 600)
SCALAR = .5
SCALAR2 = 0.2
BLUE = (0, 0, 255)

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
    
def main():
	led = 0
	rpt_mode = 0
	rumble = 0
	mesg = False

	#Connect to address given on command-line, if present
	print 'Put Wiimote in discoverable mode now (press 1+2)...'
	global wiimote
	if len(sys.argv) > 1:
            wiimote = cwiid.Wiimote(sys.argv[1])
	else:
            wiimote = cwiid.Wiimote()

	exit = 0
	wiimote.enable(cwiid.FLAG_MESG_IFC);
	rpt_mode = cwiid.RPT_IR
        wiimote.rpt_mode = rpt_mode
	while not exit:
            
            print_state(wiimote.state)
            time.sleep(1)

	wiimote.disable(cwiid.FLAG_MESG_IFC)	    
	wiimote.close()

def print_state(state):
    if 'ir_src' in state:
        valid_src = False
        print 'IR:',
        for src in state['ir_src']:
            if src:
                valid_src = True
                print src['pos'],
                
	if not valid_src:
            print 'no sources detected'
        else:
            print
    
def callback(mesg_list, time):
    L1 = []
    for mesg in mesg_list:
        if mesg[0] == cwiid.MESG_IR:
            valid_src = False
            print 'IR Report: ',
            for src in mesg[1]:
                if src:
                    valid_src = True
                    L1.append(src['pos'])

            if not valid_src:
                print 'no sources detected'
            else:
                print

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF)
resize(*SCREEN_SIZE)
init()
clock = pygame.time.Clock()


led = 0
rpt_mode = 0
rumble = 0
mesg = False

#Connect to address given on command-line, if present
print 'Put Wiimote in discoverable mode now (press 1+2)...'
global wiimote
if len(sys.argv) > 1:
    wiimote = cwiid.Wiimote(sys.argv[1])
else:
    wiimote = cwiid.Wiimote()

wiimote.enable(cwiid.FLAG_MESG_IFC);
rpt_mode = cwiid.RPT_IR
wiimote.rpt_mode = rpt_mode

wiimote.mesg_callback = callback
#while 1:
#    pass
    #print_state(wiimote.state)
    #while not l2.empty(): # needssome work
    #    pygame.draw.circle(screen, BLUE, (300,50), 20, 0)

wiimote.disable(cwiid.FLAG_MESG_IFC)
wiimote.close()

