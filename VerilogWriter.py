#!/usr/bin/env python
# PHDL VerilogWriter

import Dev
import HDLIOType
import HDLNetType
import HDLWriter

class VerilogWriter(HDLWriter.HDLWriter):
	def __init__(self,str = ""):
		Dev.Debug(Dev.Info,"VerilogWriter.__init__(self,str)")
		if str != "":
			self.Open(str)

	def WriteModule(self,module):
		module.GenerateVerilogHDL(self)

	def WriteNet(self,Name,IOType,Type,Start,End):
		Dev.Debug(Dev.Info,"VerilogWriter.WriteNet(self,Name,IOType,Type,Start,End)")
		if IOType == HDLIOType.Input:
			self.outfile.write("input")
			self.writenetcommon(Name,Start,End)
		elif IOType == HDLIOType.Output:
			self.outfile.write("output")
			self.writenetcommon(Name,Start,End)
		elif IOType == HDLIOType.InOut:
			self.outfile.write("inout")
			self.writenetcommon(Name,Start,End)
		elif IOType == HDLIOType.Wire:
			Dev.Debug(Dev.Info,"VerilogWriter.WriteNet(self,Name,IOType,Type,Start,End) -
			Skipping I/O Definition (Wire)")
		else:
			Dev.Debug(Dev.Stop,"Error: Unknown HDLIOType")
		if Type == HDLNetType.Wire:
			self.outfile.write("wire");
		elif Type == HDLNetType.Reg:
			self.outfile.write("reg\t");
		elif Type == HDLNetType.Tri:
			self.outfile.write("tri");
		elif Type == HDLNetType.Wand:
			self.outfile.write("wand");
		elif Type == HDLNetType.Wor:
			self.outfile.write("wor");
		elif Type == HDLNetType.Triand:
			self.outfile.write("triand");
		elif Type == HDLNetType.Trior:
			self.outfile.write("trior");
		elif Type == HDLNetType.Trireg:
			self.outfile.write("trireg");
		else:
			Dev.Debug(Dev.Stop,"Error: Unknown HDLNetType")
		self.writenetcommon(Name,Start,End)

	def writenetcommon(self,Name,StartIndex,EndIndex):
		Dev.Debug(Dev.Info,"VerilogWriter.writenetcommon(self,Name,StartIndex,EndIndex)")
		self.outfile.write("\t")
		if (StartIndex != EndIndex):
			self.outfile.write("[" + str(StartIndex) + ":" + str(EndIndex) + "]")
		else:
			self.outfile.write("\t")
		self.outfile.write("\t" + Name + ";\n")