#!/usr/bin/env python
# PHDL Debugging Utility Functions
# Enumeration

Debug   = 4
Info    = 3
Warning = 2
Error   = 1
Stop    = 0

# Change Me
DebugLevel = 2

# State Variables
global totalwarnings
totalwarnings = 0
global totalerrors
totalerrors = 0
global represswarning
represswarning = 0

import os

def ResetErrorCount():
	global totalwarnings
	global totalerrors
	global represswarning
	totalwarnings = 0
	totalerrors = 0
	represswarning = 0

def ShowResults(msg):
	if totalerrors == 0:
		print msg + " Completed Successfully"
	else:
		print msg + " Failed: " + str(totalerrors) + " Errors"
	if totalwarnings != 0:
		print str(totalwarnings) + " Warnings encountered"
	print ""
	if totalerrors != 0:
		os._exit(-1)

def Debug(level,msg):
	global totalwarnings
	global totalerrors
	global represswarning
	if (level == Warning) and (represswarning == 1):
		return
	if DebugLevel >= level:
		print msg
	if level == Warning:
		totalwarnings += 1
	if level == Error:
		totalerrors += 1
	if totalwarnings >= 40:
		print "Error: Too many warnings"
		os._exit(-1)
	if totalerrors >= 20:
		print "Error: Too many errors"
		os._exit(-1)
	if level == Stop:
		print "FATAL ERROR EXITTING"
		os._exit(-1)

def DisableWarnings():
	global represswarning
	represswarning = 1

def EnableWarnings():
	global represswarning
	represswarning = 0
