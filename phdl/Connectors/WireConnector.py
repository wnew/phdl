#!/usr/bin/env python
# PHDL WireConnector

from PHDL import *
import re

"""
- Consider Makeing Subwires or allowing us to get a subwire from a connector
- Warn when wires output dont explicitly state their unconnected, Error for inputs
"""
class WireConnector(Connector.Connector):

	def __init__(self,iotype = HDLIOType.Wire,type = HDLNetType.Wire,width = None):
		Dev.Debug(Dev.Info,"WireConnector.__init__(self,type,start,end)")
		self.Name = ""
		self.Comp = None
		self.Conn = None
		self.LocalConn = None
		self.IOType = iotype
		self.Type = type
		self.Width = width
		self.IsUsed = 0
		self.Anonymous = 0
		self.SubWires = { }

	def ConfigureEachOther(self,prj,v):
		if not(v.Width is None):
			if self.Width is None:
				self.Width = v.Width
				prj.AddChangedConnector(self)
			elif (self.Width != v.Width):
				Dev.Debug(Dev.Error,"Error: WireConnector " + self.Name + " in component " +
					self.Comp.InstanceName + " found an inconsistancy with Connector named " +
						v.Name + " in the configuration.")
		elif not(self.Width is None):
			v.Width = self.Width
	
	def ParameterizationCheck(self,prj):
		Dev.Debug(Dev.Info,"WireConnector.ParameterizationCheck(self)")
		if self.Width is None:
			Dev.Debug(Dev.Error,"Error: WireConnector " + self.Name + " in component " +
				self.Comp.Name + " failed to configure the width parameter.")

	def WriteIOPorts(self,hdlwriter):
		Dev.Debug(Dev.Info,"WireConnector.WriteIOPorts(self,hdlwriter)")
		# I may want to support a direction flag for these connectors
		if self.Width is None:
			Dev.Debug(Dev.Stop,"Error: WireConnector " + self.Name + " in component " +
				self.Comp.Name + " failed to configure the width parameter.")
		hdlwriter.WriteNet(self.Name,self.IOType,self.Type,self.Width - 1,0)

	def WriteIOPortNames(self,hdlwriter):
		Dev.Debug(Dev.Info,"WireConnector.WriteIOPortNames(self,hdlwriter)")
		hdlwriter.Write(self.Name)

	def WriteIOPortBindings(self,hdlwriter):
		Dev.Debug(Dev.Info,"WireConnector.WriteIOPortBindings(self,hdlwriter)")
		if self.Conn is None:
			Dev.Debug(Dev.Stop,"WireConnector " + self.Name + " in " + self.Comp.InstanceName +
				" is not connected to anything.")
		hdlwriter.Write("\t." + self.Name + "(" +
			self.Conn.LocalConnector.WriteIOPortBindingName() + ")")

	def Duplicate(self):
		Dev.Debug(Dev.Info,"WireConnector.Duplicate(self)")
		dup = WireConnector()
		dup.IOType = HDLIOType.Wire
		dup.Type = HDLNetType.Wire
		dup.Width = self.Width
		return dup

	def RenameConnector(self,newname):
		# Rename all subconnectors!
		Dev.Debug(Dev.Info,"WireConnector.RenameConnector(self,newname)")
		self.Name = newname
		newsubwires = { }
		for k,v in self.SubWires:
			# TODO: Construct new name and rename internal structure!
			v.RenameConnector(self,newname)
		# TODO: Fix Connection registration!
	
	def CreateSubconnector(self,start,end = None):
		Dev.Debug(Dev.Info,"WireConnector.CreateSubconnector(self,start,end)")
		from PHDL.Connectors.SubWireConnector import SubWireConnector
		name = ""
		if end is None:
			name = self.Name + "[" + str(start) + "]"
		else:
			name = self.Name + "[" + str(start) + ":" + str(end) + "]"
		if self.SubWires.has_key(name):
			return self.SubWires[name]
		else:
			subconn = SubWireConnector(self,self.Name,name,self.Comp,start,end)
			self.SubWires[name] = subconn
			return subconn

	def __getitem__(self, index):
		if isinstance(index,slice):
			return self.CreateSubconnector(index.start,index.stop)
		elif isinstance(index,int):
			return self.CreateSubconnector(index)
		else:
			Dev.Debug(Dev.Stop,"WireConnector: Unsupported subconnector type!")
