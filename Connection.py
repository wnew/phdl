#!/usr/bin/env python
# PHDL Connection

import Dev

class Connection:
	def __init__(self,locconn):
		Dev.Debug(Dev.Info,"Connection.__init__(self)")
		self.Connectors = { }
		self.LocalConnector = locconn

	# *INTERNAL* Attach a wire to a connector
	def Attach(self,connectionpath,connector):
		Dev.Debug(Dev.Info,"Connection.Attach(self,comp,conname)")
		self.Connectors[connectionpath + " " + connector.Name] = connector

	# *INTERNAL* Sets a connection’s anonymous flag
	def SetAnonymous(self):
		self.LocalConnector.SetAnonymous()
		return self

	# *INTERNAL* Returns the connection’s anonymous flag
	def IsAnonymous(self):
		return self.LocalConnector.IsAnonymous()

	# *INTERNAL* Reconnects all wires to a target connector
	def ReconnectTo(self,targetconnector):
		if (self.IsAnonymous() == 0):
			Dev.Debug(Dev.Stop,"Connection: Ack! I’m not an anonymous connection!")
		for k,v in self.Connectors.iteritems():
			v.Conn = targetconnector
			targetconnector.Connectors[k] = v
