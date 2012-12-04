#!/usr/bin/env python
# PHDL Connector

import Dev
import Component
import HDLIOType

class Connector(object):
	def __init__(self):
		Dev.Debug(Dev.Info,"Connector.__init__(self)")
		self.Name = ""
		self.Conn = None
		self.LocalConn = None
		self.Comp = None
		self.IsUsed = 0
		self.Anonymous = 0

	# *PUBLIC* Optional method called after a connector is attached to a component
	def LateInit(self):
		return

	# *PUBLIC* Overload how namespaces work so we can clean syntax
	def __setattr__(self,attr,val):
		Dev.Debug(Dev.Info,"Connector.__setattr__(self,attr,val)")
		self.__dict__[attr] = val

	# *PUBLIC* Overload how namespaces work so we can clean syntax
	def __getattr__(self,attr):
		Dev.Debug(Dev.Info,"Connector.__getattr__(self,attr)")
		if self.__dict__.has_key(attr):
			return self.__dict__[attr]
		else:
			Dev.Debug(Dev.Stop,"Unknown attribute: " + attr)
			return None

	# *INTERNAL* Choose a common parent!
	def ChooseCommonParent(self,b):
		if isinstance(b,int):
			# I dont actually have to create a component
			# Connect does that automatically for me!
			return a.Comp
		if (self.Comp is b.Comp) and not(b.Comp is None):
			return self.Comp
		elif (self.Comp.Parent is b.Comp) and not(b.Comp is None):
			return b.Comp
		elif (b.Comp.Parent is self.Comp) and not(self.Comp is None):
			return self.Comp
		elif (self.Comp.Parent is b.Comp.Parent) and not(self.Comp.Parent is None):
			return self.Comp.Parent
		else:
			Dev.Debug(Dev.Stop,"No common parent between wires!")

	# *PUBLIC* Add operator
	def __add__(self,b):
		adder = Components.Adder.Adder()
		self.ChooseCommonParent(b).Anonymous = adder # Bind it to an autogenerated name
		Connect(self,adder.a)
		Connect(b,adder.b)
		mywire = self.Duplicate()
		self.ChooseCommonParent(b).Anonymous = mywire
		Connect(mywire,adder.o)
		return mywire# the return value is an anonymous wire

	# *PUBLIC* Sub operator
	def __sub__(self,b):
		subtractor = Components.Sub.Sub()
		self.ChooseCommonParent(b).Anonymous = subtractor # Bind it to an autogenerated name
		Connect(self,subtractor.a)
		Connect(b,subtractor.b)
		mywire = self.Duplicate()
		self.ChooseCommonParent(b).Anonymous = mywire
		Connect(mywire,subtractor.o).SetAnonymous()
		return mywire# the return value is an anonymous wire

	# *PUBLIC Or operator
	def __or__(self,b):
		orgate = Components.Or.Or()
		self.ChooseCommonParent(b).Anonymous = orgate # Bind it to an autogenerated name
		Connect(self,orgate.a)
		Connect(b,orgate.b)
		mywire = self.Duplicate()
		self.ChooseCommonParent(b).Anonymous = mywire
		Connect(mywire,orgate.o).SetAnonymous()
		return mywire# the return value is an anonymous wire

	# *PUBLIC And operator
	def __and__(self,b):
		andgate = Components.And.And()
		self.ChooseCommonParent(b).Anonymous = andgate # Bind it to an autogenerated name
		Connect(self,andgate.a)
		Connect(b,andgate.b)
		mywire = self.Duplicate()
		self.ChooseCommonParent(b).Anonymous = mywire
		Connect(mywire,andgate.o).SetAnonymous()
		return mywire# the return value is an anonymous wire

	# *PUBLIC Xor operator
	def __xor__(self,b):
		xorgate = Components.Xor.Xor()
		self.ChooseCommonParent(b).Anonymous = xorgate # Bind it to an autogenerated name
		Connect(self,xorgate.a)
		Connect(b,xorgate.b)
		mywire = self.Duplicate()
		self.ChooseCommonParent(b).Anonymous = mywire
		Connect(mywire,xorgate.o).SetAnonymous()
		return mywire# the return value is an anonymous wire

	# Do something intelligent with shift/rotate constant -> subwire
	# otherwise instantiate a component

	# *PUBLIC* Set name of a connector
	def SetName(self,str):
		Dev.Debug(Dev.Info,"Connector.SetName(self,str)")
		self.Name = str;

	# *PUBLIC* Configure an IO Port
	def ConfigureConnector(self,prj):
		Dev.Debug(Dev.Info,"Connector.ConfigureConnector(self,prj)")
		if not(self.Conn is None):
			for k,v in self.Conn.Connectors.iteritems(): # Check type?
				self.ConfigureEachOther(prj,v)
		elif (self.IOType != HDLIOType.Wire) and (self.IsUsed == 0):
			Dev.Debug(Dev.Warning,"Warning: Connector " + self.Name +
				" is not connected to anything.")
		# Check locally connected components
		if not(self.LocalConn is None):
			for k,v in self.LocalConn.Connectors.iteritems(): # Check type?
				self.ConfigureEachOther(prj,v)

	# *PUBLIC* Exchange parameters between two connectors
	def ConfigureEachOther(self,prj,v):
		Dev.Debug(Dev.Info,"Connector.ConfigureEachOther(self,prj,v)")

	# *PUBLIC* Check the configuration just before code generation
	def ParameterizationCheck(self,prj):
		Dev.Debug(Dev.Info,"Connector.ParameterizationCheck(self,prj)")

	# *INTERNAL* Write IO Port input/output/wire/reg definitions
	def WriteIOPorts(self,hdlwriter):
		Dev.Debug(Dev.Info,"Connector.WriteIOPorts(self,hdlwriter)")

	# *INTERNAL* Write IO Port names in a comma seperated list
	def WriteIOPortNames(self,hdlwriter):
		Dev.Debug(Dev.Info,"Connector.WriteIOPortNames(self,hdlwriter)")

	# *INTERNAL* Write IO Port bindings to another module
	def WriteIOPortBindings(self,hdlwriter):
		Dev.Debug(Dev.Info,"Connector.WriteIOPortBindings(self,hdlwriter)")

	# *INTERNAL* Writes local IO Port logic to the current module
	def WriteIOPortLogic(self,hdlwriter):
		Dev.Debug(Dev.Info,"Connector.WriteIOPortLogic(self,hdlwriter)")

	# *INTERNAL* Returns binding name string
	def WriteIOPortBindingName(self,relparent = None):
		Dev.Debug(Dev.Info,"Connector.WriteIOPortBindingName(self,hdlwriter)")
		if (relparent is None) or (relparent is self.Comp):
			return self.Name
		elif (relparent is self.Comp.Parent):
			if (self.Conn is None) or (self.Conn.LocalConnector is None):
				print self.Name
				Dev.Debug(Dev.Stop,	
					"PANIC: Trying to write a binding for an unconnected connector!")
			return self.Conn.LocalConnector.Name

	# *INTERNAL* Sets the parent connector
	def Connect(self,conn):
		Dev.Debug(Dev.Info,"Connector.Connect(self,conn)")
		self.Conn = conn

	# *INTERNAL* Sets the local connector
	def SetLocalConnection(self,conn):
		Dev.Debug(Dev.Info,"Connector.SetLocalConnection(self,conn)")
		self.LocalConn = conn

	# *PUBLIC* Mark a connector as used to avoid warning messages
	# Fools us into thinking its connected
	def SetUsed(self):
		Dev.Debug(Dev.Info,"Connector.SetUsed(self)")
		self.IsUsed = 1
		return self

	# *PUBLIC* Checks if a connector is connected
	def IsConnected(self):
		Dev.Debug(Dev.Info,"Connector.IsConnected(self)")
		if (self.Conn is None) and (self.IsUsed is 0):
			return 0
		else:
			return 1

	# *PUBLIC* Removes a connector from a module
	def Remove(self):
		self.Comp.__delattr__(self.Name)

	# *PUBLIC* Sets a connector's anonymous flag
	def SetAnonymous(self):
		self.Anonymous = 1
		return self

	# *PUBLIC* Returns the connector's anonymous flag
	def IsAnonymous(self):
		return self.Anonymous

	# *INTERNAL* Duplicates a connector to create a local wire of the same type
	def Duplicate(self):
		Dev.Debug(Dev.Error, 
			"Error: Connector does not implement the Duplicate method you cannot use anonymous connections.")
