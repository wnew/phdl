#!/usr/bin/env python
# PHDL ConstantConnector
	
from PHDL import Connector
from PHDL import Dev
from PHDL import HDLIOType
from PHDL import HDLNetType
from PHDL import Util
import re
import math

"""
- Consider Makeing Subwires or allowing us to get a subwire from a connector
- Warn when wires output dont explicitly state their unconnected, Error for inputs
"""
# THIS IS VERY SKETCHY BUT IT CURRENTLY WORKS IT NEEDS A LOT OF CLEANUP
class ConstantConnector(Connector.Connector):
	def __init__(self,name,comp,value):
		Dev.Debug(Dev.Info,"ConstantConnector.__init__(self,supername,name,start,end)")
		self.Comp = comp
		self.Conn = None
		self.LocalConn = None
		self.IOType = HDLIOType.Wire
		self.Type = HDLNetType.Wire
		self.Value = value
		self.Width = None
		self.Name = name
		self.IsUsed = 1
		self.Anonymous = 0
		if not(comp is None):
			comp.AddConnector(self)

	def ConfigureEachOther(self,prj,v):
		if not(v.Width is None):
			if self.Width is None:
				self.Width = v.Width
				prj.AddChangedConnector(self)
			elif (self.Width != v.Width):
				Dev.Debug(Dev.Error,"Error: ConstantConnector " + self.Name +
					" found an inconsistancy with Local Connector named " +
					v.Name + " in the configuration.")

	def ParameterizationCheck(self,prj):
		Dev.Debug(Dev.Info,"ConstantConnector.ParameterizationCheck(self)")
		if self.Width is None:
			Dev.Debug(Dev.Error,"Error: ConstantConnector " + self.Name +
				" failed to configure the width parameter.");

	def WriteIOPorts(self,hdlwriter):
		Dev.Debug(Dev.Info,"ConstantConnector.WriteIOPorts(self,hdlwriter)")
		# I may want to support a direction flag for these connectors
		if self.Width is None:
			Dev.Debug(Dev.Stop,"Fatal Error: ConstantConnector " + self.Name +
				" was never configured with a Width.")
		#hdlwriter.WriteNet(self.Name,self.IOType,self.Type,self.Width - 1,0)
		# Add Assign Statement

	def WriteIOPortNames(self,hdlwriter):
		Dev.Debug(Dev.Info,"ConstantConnector.WriteIOPortNames(self,hdlwriter)")
		Dev.Debug(Dev.Warning,"Error: ConstantConnector cannot be used as an input/output.")

	def WriteIOPortBindings(self,hdlwriter):
		Dev.Debug(Dev.Info,"ConstantConnector.WriteIOPortBindings(self,hdlwriter)")
		hdlwriter.Write("\t." + self.Name + "(" + self.Conn.LocalName + ")")

	def WriteIOPortLogic(self,hdlwriter):
		Dev.Debug(Dev.Info,"ConstantConnector.WriteIOPortLogic(self,hdlwriter)")
	
	def WriteIOPortBindingName(self):
		Dev.Debug(Dev.Info,"ConstantConnector.WriteIOPortBindingName(self,hdlwriter)")
		return Util.VerilogBinary(self.Value,self.Width)

	def Duplicate(self):
		Dev.Debug(Dev.Info,"ConstantConnector.Duplicate(self)")
		Dev.Debug(Dev.Warning,
		"Error: ConstantConnector does not know how to duplicate itself.")
		return dup
