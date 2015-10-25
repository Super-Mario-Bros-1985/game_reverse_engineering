
from instruction import Instruction
import threading

class Block:
	NEXT_BLOCK = '_MaGiC_cOnStAnT_'
	global_id = [0]
	label_tbl = {}
	idx_tbl = {}
	lock = threading.Lock()

	def __init__(self, label = None):
		with Block.lock:
			Block.global_id[0] += 1
		self.id = Block.global_id[0]
		self.label = label
		self.instructions = []
		self._return = False
		#self._pure_return = False
		self._passthru = None
		self._branch = None
		Block.idx_tbl[self.id] = self
		if label:
			Block.label_tbl[label] = self
	def relabel(self, label):
		del Block.label_tbl[self.label]
		self.label = label
		Block.label_tbl[label] = self

	@staticmethod
	def by_id(id):
		return Block.idx_tbl[id]
	@staticmethod
	def next_id():
		return Block.global_id[0] + 1

	def __str__(self):
		if self.label:
			return 'Blk %d (%s)' % (self.id, self.label)
		else:
			return 'Blk %d' % (self.id, )
	def pp(self):
		ret = str(self)
		if self._return:
			ret += '\n\t(return)'
		else:
			ret += '\n\t-> %s' % (self.passthru(), )
		if self._branch:
			ret += '\n\t--> %s' % (self.branch(), )
		for inst in self.instructions:
			ret += '\n\t%s' % (inst, )
		return ret
	def gv(self): # for graphviz
		ret = 'Blk %d' % self.id
		if self.label:
			ret += '\n(%s)' % self.label
		if self._return:
			ret += '\nEND'
		return ret

	def append(self, inst):
		self.instructions.append(inst)

	def passthru(self):
		ret = None
		if self._passthru == Block.NEXT_BLOCK:
			ret = Block.idx_tbl[self.id + 1]
		elif self._passthru:
			ret = Block.label_tbl[self._passthru]
		return ret
	def branch(self):
		ret = None
		if self._branch:
			return Block.label_tbl[self._branch]
		return None
	def has_return(self):
		return self._return

	def set_passthru(self, pt):
		self._passthru = pt
	def set_branch(self, br):
		self._branch = br
	def set_return(self, onoff):
		self._return = onoff

