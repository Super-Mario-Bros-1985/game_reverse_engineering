#!/usr/bin/env python3

import sys

class Instruction:
	def __init__(self, opcode, oprands):
		self.opcode = opcode
		self.oprands = oprands

	def __str__(self):
		return 'Instruction %s %s' % (self.opcode, self.oprands)

class Segment:
	NEXT_SEGMENT = '_MaGiC_cOnStAnT_'
	global_id = [0]
	label_tbl = {}
	idx_tbl = {}

	_return = False
	#_pure_return = False
	_passthru = None
	_branch = None

	def __init__(self, label = None):
		self.global_id[0] += 1
		self.id = self.global_id[0]
		self.label = label
		self.instructions = []
		self.idx_tbl[self.id] = self
		if label:
			self.label_tbl[label] = self
	def relabel(self, label):
		del self.label_tbl[self.label]
		self.label = label
		self.label_tbl[label] = self

	def __str__(self):
		if self.label:
			return 'Segment %d (%s)' % (self.id, self.label)
		else:
			return 'Segment %d' % (self.id, )
	def pp(self):
		ret = str(self)
		if self._return:
			ret += '\n\t(leaf)'
		else:
			ret += '\n\t-> %s' % (self.passthru(), )
		if self._branch:
			ret += '\n\t--> %s' % (self.branch(), )
		for inst in self.instructions:
			ret += '\n\t%s' % (inst, )
		return ret

	def append(self, inst):
		self.instructions.append(inst)

	def passthru(self):
		if self._passthru == Segment.NEXT_SEGMENT:
			return self.idx_tbl[self.id + 1]
		elif self._passthru:
			return self.label_tbl[self._passthru]
		return None
	def branch(self):
		if self._branch:
			return self.label_tbl[self._branch]
		return None

f = open('GameMenuRoutine.asm', 'r')
lines = f.readlines()
segment = None

# part i - split code blocks

for line in lines:
	line = line.strip()
	idx = line.find(';') # comment
	if idx != -1:
		line = line[:idx]
	tokens = line.split()
	if len(tokens) == 0:
		continue

	label = inst = None
	if tokens[0][-1:] == ':':
		label = tokens.pop(0)[:-1]
	if len(tokens) > 0:
		opcode = tokens.pop(0)
		oprands = tokens
		inst = Instruction(opcode, oprands)

	if label:
		if segment is None: # the first run
			segment = Segment(label)
		else:
			segment._passthru = Segment.NEXT_SEGMENT
			if len(segment.instructions) == 0:
				segment.relabel(label)
			else:
				segment = Segment(label)
	elif segment is None:
		segment = Segment(label)

	if inst and inst.opcode[:1] != '.':
		segment.append(inst)
		if inst.opcode[:1] == 'b': # branch
			segment._branch = inst.oprands[0]
			segment._passthru = Segment.NEXT_SEGMENT
			segment = None
		elif inst.opcode == 'jmp': # jump
			segment._passthru = inst.oprands[0]
			segment = None
		elif inst.opcode == 'rts': # return subroutine
			segment._return = True
			segment = None

#if False:
if True:
	for id in range(1, Segment.global_id[0] + 1):
		segment = Segment.idx_tbl[id]
		print(segment.pp())


# part ii - identify branch & loop structures

max = Segment.global_id[0] + 1
reached = {}
pending = []
for id in range(1, max):
	reached[id] = set()
	pending.append(id)

while len(pending) > 0:
	id = pending.pop(0)
	reach = reached[id]
	reach = reach | set([id])
	#reached[id] = reach

	segment = Segment.idx_tbl[id]

	if segment.passthru() is None:
		continue
	passthru_id = segment.passthru().id
	passthru_reach = reached[passthru_id]
	if passthru_reach != reach | passthru_reach:
		reached[passthru_id] = reach | passthru_reach
		if passthru_id not in pending:
			pending.append(passthru_id)

	if segment.branch() is None:
		continue
	branch_id = segment.branch().id
	branch_reach = reached[branch_id]
	if branch_reach != reach | branch_reach:
		reached[branch_id] = reach | branch_reach
		if branch_id not in pending:
			pending.append(branch_id)

if False:
#if True:
	for id in range(1, max):
		print(id, reached[id])

for id in range(1, max):
	segment = Segment.idx_tbl[id]
	if segment.branch() is None:
		continue
	if id in reached[id]:
		print(id, 'loop')
	else:
		print(id, reached[segment.passthru().id] ^ reached[segment.branch().id])

