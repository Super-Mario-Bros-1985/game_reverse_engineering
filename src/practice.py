#!/usr/bin/env python3

from block import Block
import code_blocker
#from instruction import Instruction
#from segment import Segment
#import sys

#DEBUG_BLOCK = True
#DEBUG_BLOCK_GRAPHVIZ = True
#DEBUG_SEGMENT_GRAPHVIZ = True
DEBUG_SEGMENTCODE_GRAPHVIZ = True

try:
	import pygraphviz
except ImportError:
	DEBUG_GRAPHVIZ = False

f = open('GameMenuRoutine.asm', 'r')
lines = f.readlines()

# part i - split code blocks

code_blocker.split_blocks(lines)
revrefs = code_blocker.make_revrefs()

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

segments, included_in, members = code_blocker.split_segments()

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
	segments_copy = segments[:]
	segments_copy.reverse()
	for id in segments_copy:
		if id not in included_in:
			subgraph_obj[id] = g.add_subgraph(list(set(members[id])), name = 'cluster_%d' % id)
			#subgraph_obj[id] = g.add_subgraph(members[id], name = 'cluster_%d' % id)
		else:
			parent = included_in[id]
			subgraph_obj[id] = subgraph_obj[parent].add_subgraph(list(set(members[id])), name = 'cluster_%d' % id)
			#subgraph_obj[id] = subgraph_obj[parent].add_subgraph(members[id], name = 'cluster_%d' % id)

	g.layout(prog='dot')
	g.draw('segment_diagram.png')

if 'DEBUG_SEGMENTCODE_GRAPHVIZ' in globals() and DEBUG_SEGMENTCODE_GRAPHVIZ:
	g = pygraphviz.AGraph()
	
	for id in range(1, Block.next_id()):
		block = Block.by_id(id)
		label = block.gv() + '|'
		for inst in block.instructions:
			if len(inst.oprands) > 0:
				label += "%s %s\l" % (inst.opcode, inst.oprands[0])
			else:
				label += "%s\l" % (inst.opcode,)
		g.add_node(id, label = label, shape = "record")

	for id in range(1, Block.next_id()):
		block = Block.by_id(id)
		if not block.has_return():
			g.add_edge(id, block.passthru().id, dir = 'forward')
		if block.branch():
			g.add_edge(id, block.branch().id, dir = 'forward',
					color = 'blue', style = 'dashed')

	subgraph_obj = {}
	segments_copy = segments[:]
	segments_copy.reverse()
	for id in segments_copy:
		if id not in included_in:
			subgraph_obj[id] = g.add_subgraph(list(set(members[id])), name = 'cluster_%d' % id)
			#subgraph_obj[id] = g.add_subgraph(members[id], name = 'cluster_%d' % id)
		else:
			parent = included_in[id]
			subgraph_obj[id] = subgraph_obj[parent].add_subgraph(list(set(members[id])), name = 'cluster_%d' % id)
			#subgraph_obj[id] = subgraph_obj[parent].add_subgraph(members[id], name = 'cluster_%d' % id)

	g.layout(prog='dot')
	g.draw('segmentcode_diagram.png')

