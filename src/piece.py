
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

	def get_opposite_color(self):
		if not self.is_empty():
			return 'b' if self.color == 'w' else 'w'

		return None

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
		return f'{self.symbol}'
		# return f'P({self.color}, {self.type}, {self.index}, {self.symbol})'

	# used for GUI when grouping captured pieces
	def __lt__(self, other):
		order = {'p': 0, 'b': 1, 'n': 2, 'r': 3, 'q': 4, 'k': 5}
		return order[self.type] < order[other.type] 