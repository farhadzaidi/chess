
class Piece:
	def __init__(self, p_color, p_type, p_index, p_symbol):
		self.color = p_color
		self.type = p_type
		self.index = p_index
		self.symbol = p_symbol

	def is_white(self):
		return self.color == 'w'

	def is_black(self):
		return self.color == 'b'

	def is_empty(self):
		return self.color == '0'

	def same_colors(self, piece):
		if self.type == '0' or piece.type == '0':
			return False

		return self.color == piece.color

	def same_colors_or_empty(self, piece):
		if self.type == '0' or piece.type == '0':
			return True

		return self.color == piece.color

	def diff_colors(self, piece):
		if self.type == '0' or piece.type == '0':
			return False

		return self.color != piece.color

	def diff_colors_or_empty(self, piece):
		if self.type == '0' or piece.type == '0':
			return True

		return self.color != piece.color

	def __repr__(self):
		return self.symbol
