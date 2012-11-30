#!/usr/bin/env python

import sys
import os
import re

# Fix the path to be able to include PHDL core components
# For now the worst this does it include the path twice
# it shouldn’t hurt anything

sys.path.append(sys.modules.get(__name__).__path__[0] + "/../../")

# Construct the __all__ variable
__all__ = os.listdir(sys.modules.get(__name__).__path__[0])
__all__.remove(’__init__.py’)
__all__.remove(’__init__.pyc’)

for e in __all__:
	if (re.compile("[a-zA-Z0-9]*\.py$").match(e,1) is None):
		__all__.remove(e)

tmplist = [ ]

for e in __all__:
	tmp = re.split("[\.]",e)
	tmplist.append(tmp[0])

__all__ = tmplist

print "PHDL Framework: " + str(len(__all__)) + " Connectors Loaded"
