#!/usr/bin/env python
# PHDL BulkConnector

from PHDL import *
import re

"""
- Consider Makeing Subwires or allowing us to get a subwire from a connector
- Warn when wires output dont explicitly state their unconnected, Error for inputs
"""
class BulkConnector(Connector.Connector):
	def __init__(self):
		Dev.Debug(Dev.Info,"WireConnector.__init__(self,type,start,end)")
		self.Name = ""
		self.Comp = None
		self.Conn = None
		self.LocalConn = None
		self.IsUsed = 0
		self.Anonymous = 0
		self.SubWires = { }
		self.GlobalToLocal = { }
		self.LocalToGlobal = { }
		self.IOType = 0 # Bogus

	def LateInit(self):
		newsubwires = { }
		for k,v in self.SubWires.iteritems():
			newsubwires[self.Name + "_" + k] = v
			v.Name = self.Name + "_" + k
			v.Comp = self.Comp
			self.GlobalToLocal[k] = self.Name + "_" + k
			self.LocalToGlobal[self.Name + "_" + k] = k
			v.LateInit()
		self.SubWires = newsubwires
		return

	# *PUBLIC* Overload how namespaces work so we can clean syntax
	def __setattr__(self,attr,val):
		Dev.Debug(Dev.Info,"WireConnector.__setattr__(self,attr,val)")
		if isinstance(val,Connector.Connector):
			self.SubWires[attr] = val
			return
		# Default case for non-connectors
		self.__dict__[attr] = val

	# *PUBLIC* Overload how namespaces work so we can clean syntax
	def __getattr__(self,attr):
		Dev.Debug(Dev.Info,"WireConnector.__getattr__(self,attr)")
		if self.SubWires.has_key(attr):
			return self.SubWires[attr]
		elif self.SubWires.has_key(self.Name + "_" + attr):
			return self.SubWires[self.Name + "_" + attr]
		elif self.__dict__.has_key(attr):
			return self.__dict__[attr]
		else:
			print "Trying to get " + attr + " in bulkconnector " + self.Name
			Dev.Debug(Dev.Stop,"WireConnector.__getattr__(self,attr) does not exist!!!")

	# *PUBLIC* Overload how namespaces work so we can clean syntax
	def __delattr__(self,attr):
		Dev.Debug(Dev.Info,"WireConnector.__delattr__(self,attr)")
		if self.SubWires.has_key(attr):
			# This has to be cleaned up to allow connectors a chance to cleanup logic!
			del self.SubWires[attr]
			return
		Dev.Debug(Dev.Stop,"WireConnector.__delattr__: UH OH CANT DELETE!")

	# Usually this is overloaded with constraints between connectors and parameters
	def ConnectorConstraints(self,prj):
		Dev.Debug(Dev.Info,"BulkConnector.ConnectorConstraints(self,prj)")
		return

	def ConfigureEachOther(self,prj,v):
		self.ConnectorConstraints(prj) # Calling it more often than needed
		for kwire,vwire in self.SubWires.iteritems():
			# Configure connectors
			name = v.GlobalToLocal[self.LocalToGlobal[kwire]]
			vwire.ConfigureEachOther(prj,v.SubWires[name])

	# Usually this is overloaded with constraints between connectors and parameters
	def ConstraintCheck(self,prj):
		Dev.Debug(Dev.Info,"BulkConnector.ConstraintCheck(self,prj)")
		return
		# *PUBLIC* Parameterization check
	def ParameterizationCheck(self,prj):
		Dev.Debug(Dev.Info,"BulkConnector.ParameterizationCheck(self)")
		self.ConstraintCheck(prj)
		for k,v in self.SubWires.iteritems():
			# Configure connectors
			v.ParameterizationCheck(prj)

	def WriteIOPorts(self,hdlwriter):
		Dev.Debug(Dev.Info,"BulkConnector.WriteIOPorts(self,hdlwriter)")
		for k,v in self.SubWires.iteritems():
			v.WriteIOPorts(hdlwriter)

	def WriteIOPortLogic(self,hdlwriter):
		Dev.Debug(Dev.Info,"BulkConnector.WriteIOPortLogic(self,hdlwriter)")
		for k,v in self.SubWires.iteritems():
			v.WriteIOPortLogic(hdlwriter)

	def WriteIOPortNames(self,hdlwriter):
		Dev.Debug(Dev.Info,"BulkConnector.WriteIOPortNames(self,hdlwriter)")
		# Comma seperated list
		i = len(self.SubWires)
		for k,v in self.SubWires.iteritems():
			# Hack to make hiarchical BulkConnectors work
			if isinstance(v,BulkConnector):
				hdlwriter.WriteIOPortNames(hdlwriter)
			else:
				hdlwriter.Write(k)
			i = i - 1
			if (i > 0):
				hdlwriter.Write(",")

	def WriteIOPortBindings(self,hdlwriter):
		Dev.Debug(Dev.Info,"BulkConnector.WriteIOPortBindings(self,hdlwriter)")
		if self.Conn is None:
			Dev.Debug(Dev.Stop,"BulkConnector " + self.Name + " in " + self.Comp.InstanceName +
				" is not connected to anything.")
		i = len(self.SubWires)
		for kwire,vwire in self.SubWires.iteritems():
			if isinstance(vwire,BulkConnector):
				vwire.WriteIOPortBindings(hdlwriter)
			else:
				name = self.Conn.LocalConnector.GlobalToLocal[self.LocalToGlobal[kwire]]
				hdlwriter.Write("\t." + kwire + "(" +
					self.Conn.LocalConnector.SubWires[name].WriteIOPortBindingName() + ")")
				i = i - 1
				if (i > 0):
					hdlwriter.Write(",\n")
				else:
					hdlwriter.Write("\n")

	def Duplicate(self,name):
		Dev.Debug(Dev.Info,"BulkConnector.Duplicate(self)")
		dup = WireConnector(name,None)
		# Name already taken care of
		self.LocalConn = None
		# IsUsed already taken care of
		# Must map all connectors through the duplicate method!
		return dup
