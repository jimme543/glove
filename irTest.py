#!/usr/bin/python
import cwiid
import sys

    
def callback(mesg_list, time):
    L1 = []
    for mesg in mesg_list:
        # this is where i need to copy the code
	if mesg[0] == cwiid.MESG_IR:
            valid_src = False
	    #print 'IR Report: ',
	    for src in mesg[1]:
		if src:
                    valid_src = True
		    L1.append( src['pos']) #,
        if L1:
            displayList(L1)
        
def displayList(list1):
    x = 0
    y = 0
    i = 0
    for thing in list1:
        x = list1[i][0]
        y = list1[i][1]
        print "x: ", x, " y: ", y
        i += 1
    
####main()########
led = 0
rpt_mode = 0
rumble = 0
mesg = False

#Connect to address given on command-line, if present
print 'Put Wiimote in discoverable mode now (press 1+2)...'
global wiimote
if len(sys.argv) > 1:
    print "1"
    wiimote = cwiid.Wiimote(sys.argv[1])
else:
    print "2"
    wiimote = cwiid.Wiimote()

wiimote.mesg_callback = callback

wiimote.enable(cwiid.FLAG_MESG_IFC);
rpt_mode = cwiid.RPT_IR
wiimote.rpt_mode = rpt_mode
exit = 0
while 1:
    pass

wiimote.close()
