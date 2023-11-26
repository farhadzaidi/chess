
class Move:
	def __init__(self, from_index, to_index, piece, 
		captured_piece=None, special_move=None, check_index=None):
		self.from_index = from_index
		self.to_index = to_index
		self.piece = piece
		self.captured_piece = captured_piece 
		self.special_move = special_move
		self.check_index = check_index

	def __repr__(self):
		return f'{self.to_index}'
