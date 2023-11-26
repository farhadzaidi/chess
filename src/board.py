from piece import Piece
from move import Move

class Board:	
	def __init__(self):
		self.board = [
			'br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br',
			'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp',
			'00', '00', '00', '00', '00', '00', '00', '00',
			'00', '00', '00', '00', '00', '00', '00', '00',
			'00', '00', '00', '00', '00', '00', '00', '00',
			'00', '00', '00', '00', '00', '00', '00', '00',
			'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp',
			'wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr',
		]

		# board is made up of Piece objects
		# empty squares are considered pieces with no color or type
		# (denoted by '00')
		for i, piece in enumerate(self.board):
			self.board[i] = Piece(piece[0], piece[1], i, piece)

		self.castling_rights = {
			'white_short': True,
			'white_long': True,
			'black_short': True,
			'black_long': True
		}

		self.captured_pieces = {
			'w': [],
			'b': []
		}

		self.moves = []

	def make_move(self, move):
		self.moves.append(move)
		self.update_castling_rights(move)

		from_piece = self.board[move.from_index]
		to_piece = self.board[move.to_index]

		# check for en passant
		# pawn moves diagnally, but to_index is empty --> en passant
		if from_piece.is_white():
			northeast_index = move.from_index - 7
			northwest_index = move.from_index - 9
		else:
			northeast_index = move.from_index + 7
			northwest_index = move.from_index + 9

		moves_diagnal = (move.to_index == northeast_index) or (move.to_index == northwest_index)
		if from_piece.type == 'p' and to_piece.is_empty() and moves_diagnal:
			self.en_passant(move)
			return

		# check for castle
		same_side = from_piece.color == to_piece.color
		if from_piece.type == 'k' and to_piece.type == 'r' and same_side:
			self.castle(move)
			return

		# update captures
		if not to_piece.is_empty():
			self.captured_pieces[to_piece.color].append(to_piece)

		# update board
		from_piece.index = move.to_index
		self.board[move.to_index] = from_piece
		self.set_empty_square(move.from_index)

	def en_passant(self, move):
		from_piece = self.board[move.from_index]
		to_piece = self.board[move.to_index]

		# capture_index will always be directly below to_index
		capture_index = (move.to_index + 8) if move.piece.is_white() else (move.to_index - 8)
		captured_piece = self.board[capture_index]

		# update board
		from_piece.index = move.to_index 
		self.board[move.to_index] = from_piece
		self.set_empty_square(move.from_index)
		self.set_empty_square(capture_index)

		# update captures
		if move.piece.is_white():
			self.captured_pieces['b'].append(captured_piece)

	def castle(self, move):
		from_piece = self.board[move.from_index]
		to_piece = self.board[move.to_index]

		# long castle
		if move.to_index == 0 or move.to_index == 56:
			king_pos = move.from_index - 2
			rook_pos = move.to_index + 3
		# short castle
		else:
			king_pos = move.from_index + 2
			rook_pos = move.to_index - 2

		# update board
		from_piece.index = king_pos
		to_piece.index = rook_pos
		self.board[king_pos] = from_piece
		self.board[rook_pos] = to_piece
		self.set_empty_square(move.from_index)
		self.set_empty_square(move.to_index)

	def update_castling_rights(self, move):
		is_black_rook = move.piece.symbol == 'br'
		is_white_rook = move.piece.symbol == 'wr'
		is_black_king = move.piece.symbol == 'bk'
		is_white_king = move.piece.symbol == 'wk'

		if is_black_rook:
			if move.from_index == 0:
				self.castling_rights['black_long'] = False
			elif move.from_index == 7:
				self.castling_rights['black_short'] = False
		elif is_white_rook:
			if move.from_index == 56:
				self.castling_rights['white_long'] = False
			elif move.from_index == 63:
				self.castling_rights['white_short'] = False
		elif is_black_king:
			self.castling_rights['black_long'] = False
			self.castling_rights['black_short'] = False
		elif is_white_king:
			self.castling_rights['white_long'] = False
			self.castling_rights['white_short'] = False

	# HELPER FUNCTIONS

	def set_empty_square(self, index):
		self.board[index] = Piece('0', '0', index, '00')

	def __repr__(self):
		s = '\n'
		for row in range(8):
			s += f'\n\t{row + 1} | '
			for col in range(8):
				index = row * 8 + col
				s += f'{self.board[index]} '

		s += f'\n\t    a  b  c  d  e  f  g  h\n'

		return s