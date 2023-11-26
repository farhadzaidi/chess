from piece import Piece
from move_generator import MoveGenerator


class Board:
	move_generator = MoveGenerator()

	def __init__(self):
		self.initialize_board()
		self.moves = []
		self.captured_pieces = {'w': [], 'b': []}
		self.castling_rights = {
			'white_short': True,
			'white_long': True,
			'black_short': True,
			'black_long': True
		}

	def initialize_board(self):
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

		# board consists of Piece objects
		# empty squares are Piece objects with no color or type
		for i, piece in enumerate(self.board):
			self.board[i] = Piece(piece[0], piece[1], i, piece)

	def get_valid_moves(self):
		moves = Board.move_generator.generate_pseudo_legal_moves(
			self.board,
			self.castling_rights,
			self.moves[-1] if self.moves else None
		)

		return moves

	def make_move(self, move):
		self.moves.append(move)
		self.update_castling_rights(move)

		if move.special_move == 'en_passant':
			self.en_passant(move)
			return

		if move.special_move == 'castle':
			self.castle(move)
			return

		# update capture
		if move.captured_piece:
			self.captured_pieces[move.captured_piece.color].append(move.captured_piece)

		# update board
		move.piece.index = move.to_index
		self.board[move.to_index] = move.piece
		self.set_empty_square(move.from_index)

	def undo_move(self, move):
		pass

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

	def en_passant(self, move):
		# update board
		move.piece.index = move.to_index
		self.board[move.to_index] = move.piece
		self.set_empty_square(move.from_index)
		self.set_empty_square(move.captured_piece.index)

		# update capture
		self.captured_pieces[move.captured_piece.color].append(move.captured_piece)

	def castle(self, move):
		# long castle
		if move.to_index == 0 or move.to_index == 56:
			king_pos = move.from_index - 2
			rook_pos = move.to_index + 3
		# short castle
		else:
			king_pos = move.from_index + 2
			rook_pos = move.to_index - 2

		king = self.board[move.from_index]
		rook = self.board[move.to_index]

		# update board
		king.index = king_pos
		rook.index = rook_pos
		self.board[king_pos] = king
		self.board[rook_pos] = rook
		self.set_empty_square(move.from_index)
		self.set_empty_square(move.to_index)

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

		s += '\n\t    a  b  c  d  e  f  g  h\n'

		return s
