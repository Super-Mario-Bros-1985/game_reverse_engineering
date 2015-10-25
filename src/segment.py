
from block import Block
#from instruction import Instruction

class Segment:
	BRANCH = 1
	LOOP = 2
	idx_tbl = {}

	def __init__(self, type, id, destination, passthru = None, branch = None, body = None):
		self.type = type
		if type == Segment.BRANCH:
			self.id = id
			self.left = passthru
			self.right = branch
			self._passthru = destination
		elif type == Segment.LOOP:
			self.id = id
			self._passthru = destination
			self.body = body
		Segment.idx_tbl[id] = self

	@staticmethod
	def by_id(id):
		if id in Segment.idx_tbl:
			return Segment.idx_tbl[id]
		return None

	def passthru(self):
		if self._passthru in Segment.idx_tbl:
			return Segment.idx_tbl[self._passthru]
		else:
			return Block.by_id(self._passthru)
	def branch(self):
		return None
	def has_return(self):
		return False

	#@staticmethod
	#def expand_list(lst):
	#	ret = []
	#	for id in lst:
	#		ret.extend(Segment._expand_id(id))
	#	return ret
	#@staticmethod
	#def _expand_id(id):
	#	if id in Segment.idx_tbl:
	#		segment = Segment.by_id(id)
	#		if segment.type == Segment.BRANCH:
	#			members = segment.left[:]
	#			members.extend(segment.right[:])
	#			ret = Segment.expand_list(members)
	#			ret.append(segment.id)
	#			return ret
	#		elif segment.type == Segment.LOOP:
	#			members = segment.body[:]
	#			ret = Segment.expand_list(members)
	#			ret.append(segment.id)
	#			return ret
	#	else:
	#		return [id]

