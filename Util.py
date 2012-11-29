#!/usr/bin/env python
# PHDL Utility Functions

import math

# Warning unchecked width this may truncate numbers
def VerilogBinary(number,width = None):
	if width is None:
		printwidth = int(math.ceil(math.log(number+1,2)))
	else:
		printwidth = width
	if (printwidth == 0):
		printwidth = printwidth + 1
	retstr = str(printwidth) + "’b"
	for x in range(printwidth):
		retstr += str(number >> (printwidth - 1 - x) & 1)
	return retstr

# Warning unchecked width this may truncate numbers
def VerilogDecimal(number,width = None):
	return str(number)

# Warning unchecked width this may truncate numbers
def VerilogHex(number ,width = None):
	return ""
