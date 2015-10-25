
class Instruction:
	def __init__(self, opcode, oprands):
		self.opcode = opcode
		self.oprands = oprands

	def __str__(self):
		return 'Instruction %s %s' % (self.opcode, self.oprands)

