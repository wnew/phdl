#!/usr/bin/env python
__all__ = [ "Component", "ComponentImpl", "Connector", "Dev", "HDLIOType", "HDLNetType",
"HDLWriter", "Project", "Util", "VerilogWriter" ]
# Here I define all special functions like Connect
import math
"""
This is probably the most complicated single function it takes
care of all the special cases of tieing two connectors together.
Hopefully I will continue to clean it up.
"""

def connect(a,b):
	if (a is None) or (b is None):
		Dev.Debug(Dev.Error,"Connect: Trying to connect None to something!")
		return
	if isinstance(a,int) or isinstance(a,long):
		a = Connectors.ConstantConnector.ConstantConnector("CONST" + str(a),b.Comp.Parent,a)
	if isinstance(b,int) or isinstance(b,long):
		b = Connectors.ConstantConnector.ConstantConnector("CONST" + str(b),a.Comp.Parent,b)
	if (a.Comp is b.Comp):
		if not(a.Conn is None) and not(b.Conn is None):
			# Check if a connection is anonymous then rename else we make an assign
			if (a.Conn.IsAnonymous()):
				a.Comp.Parent.__delattr__(a.Conn.LocalConnector.Name)
				a.Conn.ReconnectTo(b.Conn)
				# Fix the connector!
			elif (b.Conn.IsAnonymous()):
				b.Comp.Parent.__delattr__(b.Conn.LocalConnector.Name)
				b.Conn.ReconnectTo(a.Conn)
			else:
				Dev.Debug(Dev.Stop,"Connect: Assign gen incomplete!!!")
		else:
			Dev.Debug(Dev.Stop,"Connect: Assign gen incomplete!!!!")
		return
	elif (a.Comp.Parent is b.Comp.Parent) and not(a.Comp.Parent is None):
		connectionA = a.Comp.InstanceName + ":" + a.Name
		connectionB = b.Comp.InstanceName + ":" + b.Name
		if not(a.Conn is None) and (b.Conn is None):
			conn = a.Conn
		elif not(b.Conn is None) and (a.Conn is None):
			conn = b.Conn
		elif not(a.Conn is None) and not(b.Conn is None):
			# This deals with the icky case of anonymous connector renaming!
			if (a.Conn.IsAnonymous() == 1):
				a.Comp.__delattr__(a.Name)
				a.Conn.ReconnectTo(b.Conn)
			elif (b.Conn.IsAnonymous() == 1):
				b.Comp.__delattr__(b.Name)
				b.Conn.ReconnectTo(a.Conn)
			else:
				Dev.Debug(Dev.Stop,"Connect: Assign gen incomplete!")
			return
		else:
			# Generate (unconfigured) duplicate connector
			localconnector = a.Duplicate()
			a.Comp.Parent.Anonymous = localconnector
			# Generate connection - Any assignment to Anonymous should SetAnonymous
			conn = Connection.Connection(localconnector)
			localconnector.SetLocalConnection(conn)
		a.Connect(conn)
		b.Connect(conn)
	elif (a.Comp.Parent is b.Comp) or (a.Comp is b.Comp.Parent):
		if (a.Comp is b.Comp.Parent):
			t = a
			a = b
			b = t
		connectionA = a.Comp.InstanceName + ":" + a.Name
		connectionB = b.Name
		if not(b.LocalConn is None):
			conn = b.LocalConn
		else:
			conn = Connection.Connection(b)
		if not(a.Conn is None):
			# Hard case connector renaming!
			if (a.Conn.IsAnonymous() == 1):
				a.Comp.Parent.__delattr__(a.Conn.LocalConnector.Name)
				a.Conn.ReconnectTo(conn)
			else:
				print a.Name + a.Comp.InstanceName
				Dev.Debug(Dev.Stop,"Connect: Assign gen incomplete!!")
		else:
			# Simple case a new connector!
			a.Connect(conn)
		b.SetLocalConnection(conn)
	else:
		print "Trying to connect: " + a.Comp.InstanceName + "." + a.Name + " " + b.Comp.InstanceName + "." + b.Name
		Dev.Debug(Dev.Stop,"Connect: Cannot connect connectors that are far apart!")
	conn.Attach(connectionA,a)
	conn.Attach(connectionB,b)

# Make the Connect function a builtin
__builtins__["Connect"] = connect
del connect

# Configure Rules
def configureequal(prj,obja,parama ,objb,paramb = None):
	if paramb is None:
		# Fix it to the behavior I want
		# ConfigureEqual(obja,objb,"Width") - Shorthand
		paramb = objb
		objb = parama
		parama = paramb
	if (obja.__getattr__(parama) is None) and not(objb.__getattr__(paramb) is None):
		obja.__setattr__(parama ,objb.__getattr__(paramb))
		if isinstance(obja,Connector.Connector):
			prj.AddChangedConnector(obja)
	if (objb.__getattr__(paramb) is None) and not(obja.__getattr__(parama) is None):
		objb.__setattr__(paramb ,obja.__getattr__(parama))
		if isinstance(objb,Connector.Connector):
			prj.AddChangedConnector(objb)

def configurelog2(prj,obja,parama ,objb,paramb = None):
	if paramb is None:
		# Fix it to the behavior I want
		# ConfigureLog2(obja,objb,"Width") - Shorthand
		paramb = objb
		objb = parama
		parama = paramb
	if (obja.__getattr__(parama) is None) and not(objb.__getattr__(paramb) is None):
		obja.__setattr__(parama ,int(math.ceil(math.log(objb.__getattr__(paramb),2))))
		if isinstance(obja,Connector.Connector):
			prj.AddChangedConnector(obja)
	if (objb.__getattr__(paramb) is None) and not(obja.__getattr__(parama) is None):
		objb.__setattr__(paramb ,math.pow(2,obja.__getattr__(parama)))
		if isinstance(objb,Connector.Connector):
			prj.AddChangedConnector(objb)

def configureexp2(prj,obja,parama ,objb,paramb = None):
	if paramb is None:
		# Fix it to the behavior I want
		# ConfigureExp2(obja,objb,"Width") - Shorthand
		paramb = objb
		objb = parama
		parama = paramb
	if (obja.__getattr__(parama) is None) and not(objb.__getattr__(paramb) is None):
		obja.__setattr__(parama ,int(math.pow(2,objb.__getattr__(paramb))))
		if isinstance(obja,Connector.Connector):
			prj.AddChangedConnector(obja)
	if (objb.__getattr__(paramb) is None) and not(obja.__getattr__(parama) is None):
		objb.__setattr__(paramb ,int(math.ceil(math.log(obja.__getattr__(parama),2))))
		if isinstance(objb,Connector.Connector):
			prj.AddChangedConnector(objb)



__builtins__["ConfigureEqual"] = configureequal
__builtins__["ConfigureLog2"]  = configurelog2
__builtins__["ConfigureExp2"]  = configureexp2
