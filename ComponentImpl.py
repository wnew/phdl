#!/usr/bin/env python
# PHDL ComponentImpl

import Dev
import Component

class ComponentImpl(Component.Component):
	def ParameterizationCheck(self):
		Dev.Debug(Dev.Info,"ComponentImpl.ParameterizationCheck(self)")
