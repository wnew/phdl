#!/usr/bin/env python
# PHDL SubWireConnector

from PHDL import *
#from PHDL.Connectors.WireConnector import WireConnector
import re
import math

"""
- Consider Makeing Subwires or allowing us to get a subwire from a connector
- Warn when wires output dont explicitly state their unconnected, Error for inputs
"""
class SubWireConnector(Connector.Connector):
	def __init__(self,parentcomp,supername,name,comp,start,end = None):
		Dev.Debug(Dev.Info,"SubWireConnector.__init__(self,supername,name,start,end)")
		self.Parent = parentcomp
		self.SuperName = supername
		self.Comp = comp
		self.Conn = None
		self.LocalConn = None
		self.IOType = HDLIOType.Wire
		self.Type = HDLNetType.Wire
		self.Start = start
		if (end is None):
			self.End = start
		else:
			self.End = end
		self.Width = int(math.fabs(self.Start - self.End)) + 1
		self.Name = name
		self.IsUsed = 1
		self.Anonymous = 0
		if not(comp is None):
			comp.AddConnector(self)

	def ConfigureConnector(self,prj):
		Dev.Debug(Dev.Info,"SubWireConnector.ConfigureConnector(self,prj)")
		#print self.Comp.InstanceName + ":" + self.Name
		# Check connected wires from parent component
		# Later check IO connections
		if not(self.Conn is None):
			for k,v in self.Conn.Connectors.iteritems(): # Check type?
				if not(v.Width is None):
					if self.Width is None:
						self.Width = v.Width
						prj.AddChangedConnector(self)
					elif (self.Width != v.Width):
						Dev.Debug(Dev.Error,"Error: SubWireConnector " + self.Name +
							" found an inconsistancy with Connector named " +
								v.Name + " in the configuration.")
		elif (self.IOType != HDLIOType.Wire) and (self.IsUsed == 0):
			Dev.Debug(Dev.Warning,"Warning: SubWireConnector " + self.Name +
				" is not connected to anything.")
		# Check locally connected components
		if not(self.LocalConn is None):
			for k,v in self.LocalConn.Connectors.iteritems(): # Check type?
				if not(v.Width is None):
					if self.Width is None:
						self.Width = v.Width
						prj.AddChangedConnector(self)
					elif (self.Width != v.Width):
						Dev.Debug(Dev.Error,"Error: SubWireConnector " + self.Name +
							" found an inconsistancy with Local Connector named " +
								v.Name + " in the configuration.")

	def ParameterizationCheck(self,prj):
		Dev.Debug(Dev.Info,"SubWireConnector.ParameterizationCheck(self)")
		if self.Width is None:
			Dev.Debug(Dev.Error,"Error: SubWireConnector " + self.Name +
				" failed to configure the width parameter.");

	def WriteIOPorts(self,hdlwriter):
		Dev.Debug(Dev.Info,"SubWireConnector.WriteIOPorts(self,hdlwriter)")
		# I may want to support a direction flag for these connectors
		if self.Width is None:
			Dev.Debug(Dev.Stop,"Fatal Error: SubWireConnector " + self.Name +
				" was never configured with a Width.")
		#hdlwriter.WriteNet(self.Name,self.IOType,self.Type,self.Width - 1,0)
		# Add Assign Statement

	def WriteIOPortNames(self,hdlwriter):
		Dev.Debug(Dev.Info,"SubWireConnector.WriteIOPortNames(self,hdlwriter)")
		hdlwriter.Write(self.Name)

	def WriteIOPortBindings(self,hdlwriter):
		Dev.Debug(Dev.Info,"SubWireConnector.WriteIOPortBindings(self,hdlwriter)")
		if self.Conn is None:
			Dev.Debug(Dev.Stop,"SubWireConnector " + self.Name + " in " +
				self.Comp.InstanceName + " is not connected to anything.")
		hdlwriter.Write("\t." + self.Name + "(" +
			self.Conn.LocalConnector.WriteIOPortBindingName() + ")")
	
	def WriteIOPortLogic(self,hdlwriter):
		Dev.Debug(Dev.Info,"SubWireConnector.WriteIOPortLogic(self,hdlwriter)")

	def WriteIOPortBindingName(self,relparent = None):
		Dev.Debug(Dev.Info,"Connector.WriteIOPortBindingName(self,hdlwriter)")
		if (relparent is None) or (relparent is self.Parent.Comp):
			return self.Name
		elif (relparent is self.Comp.Parent):
			if (self.Parent.Conn is None) or (self.Parent.Conn.LocalConnector is None):
				Dev.Debug(Dev.Stop,
					"PANIC: Trying to write a binding for an unconnected connector!")
			if (self.Width == 1):
				return self.Parent.Conn.LocalConnector.Name + "[" + str(self.Start) + "]"
			else:
				return self.Parent.Conn.LocalConnector.Name + "[" + str(self.Start) + ":" +
					str(self.End) + "]"

	def Duplicate(self):
		Dev.Debug(Dev.Info,"WireConnector.Duplicate(self)")
		from PHDL.Connectors.WireConnector import WireConnector
		dup = WireConnector()
		# IsUsed already taken care of
		dup.IOType = HDLIOType.Wire
		dup.Type = HDLNetType.Wire
		dup.Width = self.Width
		return dup
