#!/usr/bin/env python
# PHDL Component

import re
import Dev
import Connection
import HDLIOType
import Connector

class Component(object):
	"""Component Class
	All PHDL components are built upon this class. This takes
	care of a lot of the tedious work of building a component.
	It also manages I/O and code generation. It provides a generic API for that.
	"""
	def __init__(self,name = None,instancename = None):
		Dev.Debug(Dev.Info,"Component.__init__(self)")
		self.Init(name,instancename)

	# *PUBLIC* Initializes the component
	def Init(self,name = None,instancename = None):
		self.Instance = None
		self.MetaInstance = self
		self.Parent = None
		self.Name = name
		if not(self.__dict__.has_key("InstanceName")):
			self.InstanceName = instancename
		self.Connectors = [ ]
		self.Components = { }
		self.NetNameNumber = 0
		self.CompNameNumber = 0
		self.DelayedAutoConnect = { }

	# *PUBLIC* Initializes the instance of this component
	def InitInstance(self):
		# These two variables form the linked list that provide our view
		# of namespaces.
		self.Instance.Instance = self.Instance
		self.Instance.MetaInstance = self
		self.Instance.InitLogic()

	def InitLogic(self):
		Dev.Debug(Dev.Info,"Component.InitLogic(self)")

	# *PUBLIC* Overload how namespaces work so we can clean syntax
	def __setattr__(self,attr,val):
		Dev.Debug(Dev.Info,"Component.__setattr__(self,attr,val)")
		# Attempts to set anonymous turn into an auto-generated name!
		if attr == "Anonymous":
			if isinstance(val,Component):
				val.Instance = None
				val.MetaInstance = val
				val.InstanceName = self.GenerateComponentName()
				val.Parent = self.GetMetaInstance()
				self.AddSubcomponent(val)
			elif isinstance(val,Connector.Connector):
				val.Name = self.GenerateNetName()
				val.Comp = self.GetMetaInstance()
				val.SetAnonymous()
				val.LateInit()
				self.AddConnector(val)
			else:
				Dev.Debug(Dev.Stop,"Error self.Anonymous is a reserved variable name!")
			return
		if isinstance(val,Component) and (attr != "Instance") and (attr != "MetaInstance") and (attr != "Parent"):
			#val.Init(instancename = attr)
			val.Instance = None
			val.MetaInstance = val
			val.InstanceName = attr
			val.Parent = self.GetMetaInstance()
			self.AddSubcomponent(val)
			return
		if isinstance(val,Connector.Connector):
			# If the connector exists then we run Connect!
			# If you want to overwrite a connector you must delete it first
			# so as to unbind it properly from the current Connector!
			if not(self.GetConnector(attr) is None):
				# Maybe I should check for autogen names but I think were ok!
				# At least throw an error
				# TODO: Make sure this throughs an error when its not possible(currently)
				Connect(self.GetConnector(attr),val)
			else:
				val.Name = attr
				val.Comp = self.GetMetaInstance()
				val.LateInit()
				self.AddConnector(val)
			return
		# Default case for non-special components/connectors
		# Modify all special variables to by tied between shell/instance
		if not(self.MetaInstance is self) and (attr != "Instance") and (attr != "MetaInstance"):
			self.MetaInstance.__setattr__(attr,val)
		else:
			self.__dict__[attr] = val

	# *PUBLIC* Overload how namespaces work so we can clean syntax
	def __getattr__(self,attr):
		Dev.Debug(Dev.Info,"Component.__getattr__(self,attr)")
		# Avoid Infinite Recursion on Initialization
		if (attr == "MetaInstance"):
			return None
		# Modify all special variables to by tied between meta/instance
		if not(self.MetaInstance is self) and not(self.MetaInstance is None):
			return self.MetaInstance.__getattr__(attr)
		elif self.MetaInstance is self:
			if self.__dict__.has_key(attr):
				return self.__dict__[attr]
		if not(self.GetSubcomponent(attr) is None):
			return self.GetSubcomponent(attr)
		if not(self.GetConnector(attr) is None):
			return self.GetConnector(attr)
		print "Trying to get " + attr + " in component " + self.InstanceName
		Dev.Debug(Dev.Stop,"Component.__getattr__(self,attr) does not exist!!!")

	# *PUBLIC* Overload how namespaces work so we can clean syntax
	def __delattr__(self,attr):
		Dev.Debug(Dev.Info,"Component.__delattr__(self,attr)")
		if not(self.GetConnector(attr) is None):
			# This has to be cleaned up to allow connectors a chance to cleanup logic!
			self.Connectors.remove(self.GetConnector(attr))
			return
		Dev.Debug(Dev.Stop,"Component.__delattr__: UH OH CANT DELETE!")
		# We can not delete components yet!

	# *INTERNAL* Used to add all subcomponents to the project for generation phase
	def AddBindings(self,project):
		"""Adds Bindings to a project
		test
		"""
		Dev.Debug(Dev.Info,"Component.AddBindings(self,project)")
		project.AddComponent(self)
		for k, v in self.Components.iteritems():
			v.AddBindings(project)

	# *INTERNAL* Adds a connector to self
	def AddConnector(self,con):
		Dev.Debug(Dev.Info,"Component.AddConnector(self,con)")
		# Check for duplicate connectors
		self.Connectors.append(con)

	# *INTERNAL* Gets a connector from self
	def GetConnector(self,conname):
		Dev.Debug(Dev.Info,"Component.GetConnector(self,conname)")
		for e in self.Connectors: # Normal connectors Including Subconnectors
			if e.Name == conname:
				return e;
		return None

	# *INTERNAL* Adds a subcomponent to self
	def AddSubcomponent(self,comp):
		Dev.Debug(Dev.Info,"Component.AddSubcomponent(self,comp)")
		self.Components[comp.InstanceName] = comp
		comp.AutoConnectInternal()

	# *INTERNAL* Gets a subcomponent from self
	def GetSubcomponent(self,compname):
		Dev.Debug(Dev.Info,"Component.AddSubcomponent(self,compname)")
		splitcomponentname = re.split("[\.]",compname,1)
		if self.Components.has_key(splitcomponentname[0]):
			if len(splitcomponentname) == 1:
				retvalue = self.Components[splitcomponentname[0]]
				if not(retvalue.Instance is None) and (retvalue.Instance != retvalue):
					return retvalue.Instance
				else:
					return retvalue
			else:
				return self.Components[splitcomponentname[0]].GetSubcomponent(splitcomponentname[1])
		else:
			return None

	# *PUBLIC* Allows you to iterate over a pattern of connectors
	def ConnectorIterator(self,pattern = "."):
		cons = []
		for e in self.Connectors:
			if re.match(pattern,e.Name,1):
				cons.append(e)
		return cons

	# *PUBLIC* Allows you to iterate over a pattern of components
	def ComponentIterator(self,pattern = "."):
		cons = []
		for k,v in self.Components.iteritems():
			if re.match(pattern,k,1):
				cons.append(v)
		return cons

	# *PUBLIC* Saves dictionary of connections
	def AutoConnect(self,wiredictionary):
		self.DelayedAutoConnect = wiredictionary

	# *INTERNAL* Used to autoconnect wires after component is attached
	def AutoConnectInternal(self):
		for k,v in self.DelayedAutoConnect.iteritems():
			for e in self.Connectors:
				if (k == e.Name):
					Connect(v,e)
		return

	"""ConfigureComponent(self) - Configures the local component and its subcomponents
	This method configures all connectors and then components. The implementation of this
	method must select our optimimum instance (Allow it to add new components), configure
	connectors, and configure any subcomponents.
	"""
	def ConfigureComponent(self,prj):
		Dev.Debug(Dev.Info,"Component.ConfigureComponent(self)")
		self.Instance = self
		for e in self.Connectors:
			e.ConfigureConnector(prj)
		for k,v in self.Components.iteritems():
			v.ConfigureComponent(prj)
		if self.Name is None:
			self.GenerateName(prj);

	# Last minute configuration check
	# This reports errors and warnings
	def ParameterizationCheck(self,prj):
		Dev.Debug(Dev.Info,"Component.ParameterizationCheck(self,prj)")
		for e in self.Connectors:
			e.ParameterizationCheck(prj)
		for k,v in self.Components.iteritems():
			v.ParameterizationCheck(prj)

	def GetInstance(self):
		Dev.Debug(Dev.Info,"Component.GetInstance(self)")
		if (self.Instance is None):
			Dev.Debug(Dev.Error,"Error: Unconfigured component " + self.InstanceName)
		else:
			return self.Instance

	def GetMetaInstance(self):
		Dev.Debug(Dev.Info,"Component.GetMetaInstance(self)")
		if (self.MetaInstance is self):
			return self
		else:
			return self.MetaInstance.GetMetaInstance()

	# For Input/Output Lists I need to build the list first
	# then write the list out in order to properly solve the comma problem
	def GenerateVerilogHDLHeader(self,hdlwriter):
		Dev.Debug(Dev.Info,"Component.GenerateVerilogHDLHeader(self,hdlwriter)")
		if self.Name is None:
			Dev.Debug(Dev.Stop,"PANIC: self.Name is not set in instance " + self.InstanceName)
		hdlwriter.Write("module " + self.Name + "(")
		i = 0
		for e in self.Connectors:
			if e.IOType != HDLIOType.Wire:
				i = i + 1
		for e in self.Connectors:
			if e.IOType != HDLIOType.Wire:
				e.WriteIOPortNames(hdlwriter)
				i = i - 1
				if i != 0:
					hdlwriter.Write(",")
		hdlwriter.Write(");\n");
		for e in self.Connectors:
			e.WriteIOPorts(hdlwriter)
		hdlwriter.Write("\n");
		for e in self.Connectors:
			e.WriteIOPortLogic(hdlwriter)
		for k,v in self.Components.iteritems():
			hdlwriter.Write("\n" + v.Name + " " + v.InstanceName + "(\n")
			i = 0
			for c in v.Connectors:
				if c.IOType != HDLIOType.Wire:
					i = i + 1
			for c in v.Connectors:
				if c.IOType != HDLIOType.Wire:
					i = i - 1
					c.WriteIOPortBindings(hdlwriter)
					if i != 0:
						hdlwriter.Write(",\n")
			hdlwriter.Write("\n);\n")

	def GenerateVerilogHDLBody(self,hdlwriter):
		Dev.Debug(Dev.Info,"Component.GenerateVerilogHDLBody(self,hdlwriter)")
		if not(self.Parent is None):
			Dev.Debug(Dev.Warning,"Warning: " + self.InstanceName + " has no local code.")
			hdlwriter.Write("\n\t// No Body\n");

	def GenerateVerilogHDLFooter(self,hdlwriter):
		Dev.Debug(Dev.Info,"Component.GenerateVerilogHDLFooter(self,hdlwriter)")
		hdlwriter.Write("endmodule\n\n\n")

	def GenerateVerilogHDL(self,hdlwriter):
		Dev.Debug(Dev.Info,"Component.GenerateVerilogHDL(self,hdlwriter)")
		self.GenerateVerilogHDLHeader(hdlwriter)
		self.GenerateVerilogHDLBody(hdlwriter)
		self.GenerateVerilogHDLFooter(hdlwriter)

	def GenerateVHDLHeader(self,hdlwriter):
		Dev.Debug(Dev.Stop,"Component.GenerateVHDLHeader(self,hdlwriter) NOT IMPLEMENTED")

	def GenerateVHDLBody(self,hdlwriter):
		Dev.Debug(Dev.Stop,"Component.GenerateVHDLBody(self,hdlwriter) NOT IMPLEMENTED")

	def GenerateVHDLFooter(self,hdlwriter):
		Dev.Debug(Dev.Stop,"Component.GenerateVHDLFooter(self,hdlwriter) NOT IMPLEMENTED")

	def GenerateVHDL(self,hdlwriter):
		Dev.Debug(Dev.Info,"Component.GenerateVerilogHDL(self,hdlwriter)")
		self.GenerateVHDLHeader(hdlwriter)
		self.GenerateVHDLBody(hdlwriter)
		self.GenerateVHDLFooter(hdlwriter)

	def GenerateNetName(self):
		Dev.Debug(Dev.Info,"HDLComponent.GenerateNetName(self)")
		tmpstr = "net" + str(self.NetNameNumber)
		self.NetNameNumber += 1
		return tmpstr

	def GenerateComponentName(self):
		Dev.Debug(Dev.Info,"HDLComponent.GenerateComponentName(self)")
		tmpstr = "comp" + str(self.CompNameNumber)
		self.CompNameNumber += 1
		return tmpstr

	def GenerateName(self,prj = None):
		Dev.Debug(Dev.Info,"HDLComponent.GenerateName(self)")
		if (self.Parent is None):
			# We are an unnamed main component just set the name to maincomponent
			self.Name = "maincomponent"
		elif not(prj is None):
			# Get a global name unique from the project
			if self.Name is None:
				self.Name = prj.GenerateComponentTypeName()
		else:
			Dev.Debug(Dev.Stop,"Error GenerateName must be implemented or something.")
		return self.Name
