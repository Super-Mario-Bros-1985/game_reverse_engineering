#!/usr/bin/env python3

from block import Block
from instruction import Instruction
from segment import Segment
import sys

#DEBUG_BLOCK = True
#DEBUG_BLOCK_GRAPHVIZ = True
DEBUG_SEGMENT_GRAPHVIZ = True

try:
	import pygraphviz
except ImportError:
	DEBUG_GRAPHVIZ = False

f = open('GameMenuRoutine.asm', 'r')
lines = f.readlines()
block = None

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
		if block is None: # the first run
			block = Block(label)
		else:
			block.set_passthru(Block.NEXT_BLOCK)
			if len(block.instructions) == 0:
				block.relabel(label)
			else:
				block = Block(label)
	elif block is None:
		block = Block(label)

	if inst and inst.opcode[:1] != '.':
		block.append(inst)
		if inst.opcode[:1] == 'b': # branch
			block.set_branch(inst.oprands[0])
			block.set_passthru(Block.NEXT_BLOCK)
			block = None
		elif inst.opcode == 'jmp': # jump
			block.set_passthru(inst.oprands[0])
			block = None
		elif inst.opcode == 'rts': # return subroutine
			block.set_return(True)
			block = None

if 'DEBUG_BLOCK' in globals() and DEBUG_BLOCK:
	for id in range(1, Block.next_id()):
		block = Block.by_id(id)
		print(block.pp())

if 'DEBUG_BLOCK_GRAPHVIZ' in globals() and DEBUG_BLOCK_GRAPHVIZ:
	g = pygraphviz.AGraph()
	
	for id in range(1, Block.next_id()):
		block = Block.by_id(id)
		if block.has_return():
			g.add_node(block.gv())
		else:
			g.add_edge(block.gv(), block.passthru().gv(), dir = 'forward')
		if block.branch():
			g.add_edge(block.gv(), block.branch().gv(), dir = 'forward',
					color = 'blue', style = 'dashed')

	g.layout(prog='dot')
	g.draw('block_diagram.png')

# part ii - identify branch & loop structures

def identify_structure(blocks):
	remaining_blocks = blocks[:]
	last_blocks = None
	segments = []
	included_in = {} # for Graphviz
	members = {} # for Graphviz

	while remaining_blocks:
		if remaining_blocks == last_blocks:
			break
		last_blocks = remaining_blocks[:]

		for id in remaining_blocks:
			ret = identify_block(id)
			if ret[0] == 'NOTHING':
				remaining_blocks.remove(id)
			elif ret[0] == 'BRANCH':
				new_segment(
					Segment(Segment.BRANCH, id, ret[3],
							passthru = ret[1], branch = ret[2]),
					segments, included_in, members)
				for z in ret[1]:
					if z in remaining_blocks:
						remaining_blocks.remove(z)
				for z in ret[2]:
					if z in remaining_blocks:
						remaining_blocks.remove(z)
				remaining_blocks.remove(id)
			elif ret[0] == 'LOOP' and ret[1] == 'passthru':
				new_segment(
					Segment(Segment.LOOP, Block.by_id(id).passthru().id,
							Block.by_id(id).branch().id, body = ret[2]),
					segments, included_in, members)
				remaining_blocks.remove(id)
			elif ret[0] == 'LOOP' and ret[1] == 'branch':
				new_segment(
					Segment(Segment.LOOP, Block.by_id(id).branch().id,
							Block.by_id(id).passthru().id, body = ret[2]),
					segments, included_in, members)
				remaining_blocks.remove(id)
	return segments, included_in, members

def new_segment(segment, segments, included_in, members):
	id = segment.id
	segments.append(segment.id)

	m = []
	if segment.type == Segment.BRANCH:
		m = segment.left[:]
		m.extend(segment.right[:])
	elif segment.type == Segment.LOOP:
		m = segment.body[:]

	sm = []
	for block_id in m:
		if Segment.by_id(block_id):
			if block_id not in included_in: # temporary
				included_in[block_id] = id
			sm.extend(members[block_id])
			sm.remove(block_id) # remove dup
	
	m.append(id)
	m.extend(sm)
	members[id] = m
	
def identify_block(id):
	block = Block.by_id(id)

	left, left_branch = travel_path(id, block.passthru().id)
	right, right_branch = travel_path(id, block.branch().id)

	if id == left[len(left) - 1]:
		return ['LOOP', 'passthru', left[1:]]
	if id == right[len(right) - 1]:
		return ['LOOP', 'branch', right[1:]]
	both = set(left) & set(right)
	if len(both) > 0:
		common = None
		for e in left:
			if e in both:
				common = e
				break
		return ['BRANCH', left[:left.index(common)], right[:right.index(common)], common]
	if left_branch or right_branch:
		return ['HAS_BRANCH']
	return ['NOTHING']

def travel_path(origin_id, start_id):
	path = []
	branch_encounted = False
	head = start_id
	while True:
		path.append(head)
		b = Segment.by_id(head)
		if not b:
			b = Block.by_id(head)
		if origin_id == head:
			break
		if b.has_return():
			break
		if b.branch() and not b.branch().has_return():
			branch_encounted = True
			break
		head = b.passthru().id
	return path, branch_encounted
	
blocks_to_identify = []

for id in range(1, Block.next_id()):
	block = Block.by_id(id)
	if block.branch():
		blocks_to_identify.append(id)

segments, included_in, members = identify_structure(blocks_to_identify)

if 'DEBUG_SEGMENT_GRAPHVIZ' in globals() and DEBUG_SEGMENT_GRAPHVIZ:
	g = pygraphviz.AGraph()
	
	for id in range(1, Block.next_id()):
		block = Block.by_id(id)
		g.add_node(id, label = block.gv())

	for id in range(1, Block.next_id()):
		block = Block.by_id(id)
		if not block.has_return():
			g.add_edge(id, block.passthru().id, dir = 'forward')
		if block.branch():
			g.add_edge(id, block.branch().id, dir = 'forward',
					color = 'blue', style = 'dashed')

	subgraph_obj = {}
	segments.reverse()
	for id in segments:
		if id not in included_in:
			subgraph_obj[id] = g.add_subgraph(list(set(members[id])), name = 'cluster_%d' % id)
			#subgraph_obj[id] = g.add_subgraph(members[id], name = 'cluster_%d' % id)
		else:
			parent = included_in[id]
			subgraph_obj[id] = subgraph_obj[parent].add_subgraph(list(set(members[id])), name = 'cluster_%d' % id)
			#subgraph_obj[id] = subgraph_obj[parent].add_subgraph(members[id], name = 'cluster_%d' % id)

	g.layout(prog='dot')
	g.draw('segment_diagram.png')

