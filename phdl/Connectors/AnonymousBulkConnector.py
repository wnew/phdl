#!/usr/bin/env python
# PHDL AnonymousBulkConnector

from PHDL import *
import re

"""
- Consider Makeing Subwires or allowing us to get a subwire from a connector
- Warn when wires output dont explicitly state their unconnected, Error for inputs
"""

def getportbindingname(x,relparent):
	if (isinstance(x[1],int) or isinstance(x[1],long)):
		return Util.VerilogBinary(x[1],x[0])
	else:
		if x[0] == 1:
			return x[1].WriteIOPortBindingName(relparent)
		else:
			return "{" + str(x[0]) + "{" + x[1].WriteIOPortBindingName(relparent) + "}}"

class AnonymousBulkConnector(Connector.Connector):
	def __init__(self,*cons):
		Dev.Debug(Dev.Info,"AnonymousBulkConnector.__init__(self)")
		self.Name = ""
		self.Comp = None
		self.Conn = None
		self.LocalConn = None
		self.IOType = HDLIOType.Wire
		self.Type = HDLNetType.Wire
		self.Width = None
		self.IsUsed = 0
		self.Anonymous = 0
		self.BundledWires = [ ]
		self.SubWires = { } # I need to support subwires!
		for e in cons:
			if isinstance(e,tuple):
				self.Add(e[0],e[1])
			else:
				self.Add(e)
	
	# Overload the methods to allow adding connectors
	"""
	This needs work it has to be improved to support the situations better
	also it may have buggness
	"""
	def ConfigureConnector(self,prj):
		Dev.Debug(Dev.Info,"AnonymousBulkConnector.ConfigureConnector(self,prj)")
		# Calculate the total Width
		# We only care about the inputs that were added because
		# there is no way to solve the 1 to N mapping
		width = 0
		for i in self.BundledWires:
			if (isinstance(i[1],Connector.Connector) and (i[1].Width is None)):
				width = None
			elif not(width is None):
				if (isinstance(i[1],int) or isinstance(i[1],long)):
					width = width + i[0]
				else:
					width = width + (i[0] * i[1].Width)
		self.Width = width

	def ParameterizationCheck(self,prj):
		Dev.Debug(Dev.Info,"AnonymousBulkConnector.ParameterizationCheck(self)")

	def WriteIOPorts(self,hdlwriter):
		Dev.Debug(Dev.Info,"AnonymousBulkConnector.WriteIOPorts(self,hdlwriter)")

	def WriteIOPortNames(self,hdlwriter):
		Dev.Debug(Dev.Info,"AnonymousBulkConnector.WriteIOPortNames(self,hdlwriter)")

	def WriteIOPortBindings(self,hdlwriter):
		Dev.Debug(Dev.Info,"AnonymousBulkConnector.WriteIOPortBindings(self,hdlwriter)")

	def WriteIOPortBindingName(self):
		Dev.Debug(Dev.Info,"Connector.WriteIOPortBindingName(self,hdlwriter)")
		comps = [ ]
		for i in range(len(self.BundledWires)):
			comps.append(self.Comp)
		str = "{" + ",".join(map(getportbindingname,self.BundledWires,comps)) + "}"
		return str

	def Duplicate(self,name):
		Dev.Debug(Dev.Stop,"AnonymousBulkConnector.Duplicate(self) Not Implemented")

	def Add(self,conn,count = 1):
		Dev.Debug(Dev.Info,"AnonymousBulkConnector.Add(self)")
		self.BundledWires.append((count,conn))

