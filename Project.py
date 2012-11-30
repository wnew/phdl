#!/usr/bin/env python
# PHDL Project

import Dev
import Component

"""
Project Parameters:
TARGET:
* XILINX_SPARTAN
* XILINX_SPARTAN2
* XILINX_SPARTAN3
* XILINX_VIRTEX
* XILINX_VIRTEX2
* XILINX_VIRTEX2PRO
* XILINX_VIRTEX3
* XILINX_VIRTEX4
* RTL
* SIM
GOAL:
* SIZE
* SPEED
* POWER
"""

class Project:
	def __init__(self,cirname = ""):
		Dev.Debug(Dev.Info,"Project.__init__(self)")
		self.Name = cirname
		self.UnconfiguredComponents = { }
		self.Components = { }
		self.MainComponentInstance = None
		self.MainComponentName = ""
		self.MultipleFiles = 0
		self.Parameters = { }
		self.ChangedComponents = { }
		self.CompNameNumber = 0

	# Component Interface
	def AddComponent(self,comp):
		Dev.Debug(Dev.Info,"Project.AddComponent(self,typename,comp)")
		self.UnconfiguredComponents[comp] = comp

	def RemoveComponent(self,comp):
		Dev.Debug(Dev.Info,"Project.RemoveComponent(self,typename,comp)")

	#del self.UnconfiguredComponents = comp
	def SetMainComponent(self,instance):
		Dev.Debug(Dev.Info,"Project.SetMainComponent(self,typename)")
		iterations = 0
		self.MainComponentInstance = instance
		TmpComponents = { }
		# New Auto-Configuration Method
		self.MainComponentInstance.AddBindings(self)
		TmpComponents = self.UnconfiguredComponents
		while len(TmpComponents) != 0:
			print "Iteration " + str(iterations) + ": " + str(len(TmpComponents)) +
				" Changed Components"
			self.ChangedComponents.clear()
			# - Add all components to the change list
			for c in TmpComponents:
				c.ConfigureComponent(self)
			if (iterations == 0):
				Dev.DisableWarnings()
			TmpComponents = self.ChangedComponents.values()
			iterations += 1
			if iterations > 50:
				Dev.Debug(Dev.Stop, "Project needs more than 50 iterations to solve please check that there are no bugs.")
		Dev.EnableWarnings()
		self.MainComponentInstance.AddBindings(self)
		self.MainComponentInstance.ParameterizationCheck(self)

	# Generation Control
	def SetMultifileGeneration(self,tf):
		Dev.Debug(Dev.Info,"Project.SetMultifileGeneration(self,tf)")
		self.MultipleFiles = tf

	def GenerateHDL(self,hdlwriter):
		Dev.Debug(Dev.Info,"Project.GenerateHDL(self,hdlwriter)")
		for k,v in self.UnconfiguredComponents.iteritems():
			tmp = v.GetInstance()
			self.Components[tmp.Name] = tmp
		Dev.Debug(Dev.Info,"Project.GenerateHDL(self)")
		if self.MultipleFiles == 0:
			hdlwriter.Write("// "+self.Name+" Project\n\n")
		# Generate components
		for k, v in self.Components.iteritems():
			if not(v is self.MainComponentInstance):
				if self.MultipleFiles == 1:
					hdlwriter.Open(k + ".v") # language dep
					if self.Name != "":
						hdlwriter.Write("// Subcomponent Component: "+self.Name+" Project\n\n")
					hdlwriter.WriteModule(v)
					if self.MultipleFiles == 1:
						hdlwriter.Close()
		# Generate top component
		if self.MultipleFiles == 1:
			hdlwriter.Open(self.MainComponentInstance.Name + ".v") # language dep
			if self.Name != "":
				hdlwriter.Write("// Main Component: "+self.Name+" Project\n\n")
		hdlwriter.WriteModule(self.MainComponentInstance)
		if self.MultipleFiles == 1:
			hdlwriter.Close()

	# Global Parameter Control
	def SetParameter(self,param,value):
		Dev.Debug(Dev.Info,"Project.SetParameter(self,param,value)")
		self.Parameters[param] = value

	def GetParameter(self,param):
		Dev.Debug(Dev.Info,"Project.GetParameter(self,param)")
		return self.Parameters[param]

	# Auto-Configuration Control
	def AddChangedComponent(self,comp):
		Dev.Debug(Dev.Info,"Project.AddChangedComponent(self,comp)")
		self.ChangedComponents[id(comp)] = comp;

	def AddChangedConnector(self,conn):
		Dev.Debug(Dev.Info,"Project.AddChangedConnector(self,conn)")
		self.AddChangedComponent(conn.Comp)
		if not(conn.Conn is None):
			for k, v in conn.Conn.Connectors.iteritems():
				self.AddChangedComponent(v.Comp);
		if not(conn.LocalConn is None):
			for k, v in conn.LocalConn.Connectors.iteritems():
				self.AddChangedComponent(v.Comp);

	def GenerateComponentTypeName(self):
		Dev.Debug(Dev.Info,"Project.GenerateComponentTypeName(self)")
		tmpstr = "CompType" + str(self.CompNameNumber)
		self.CompNameNumber += 1
		return tmpstr
		