
class Move:

	def __init__(self, from_index, to_index, piece, special_move=None):
		self.from_index = from_index
		self.to_index = to_index
		self.piece = piece
		self.special_move = special_move