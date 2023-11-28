from piece import Piece
from move_generator import MoveGenerator


class Board:
	move_generator = MoveGenerator()

	def __init__(self):
		self.initialize_board()
		self.moves = []
		self.undone_moves = []
		self.captured_pieces = {'w': [], 'b': []}
		self.castling_rights = {
			'w_short': True,
			'w_long': True,
			'b_short': True,
			'b_long': True
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

	def update_castling_rights(self, move, undo=False):
		if undo:
			if move.updated_castling_rights:
				for right in move.updated_castling_rights:
					self.castling_rights[right] = True
				move.updated_castling_rights = None
			return
			
		rights = []
		castling_indices = {0: 'b_long', 7: 'b_short', 56: 'w_long', 63: 'w_short'}

		# revoke castling rights if rook moves
		if move.from_index in castling_indices:
			rights.append(castling_indices[move.from_index])

		# revoke castling rights if rook gets captured
		if move.to_index in castling_indices:
			rights.append(castling_indices[move.to_index])

		# revoke castling rights if king moves
		if move.piece.symbol == 'bk' or move.piece.symbol == 'wk':
			color = move.piece.color
			rights.extend([f'{color}_long', f'{color}_short'])

		# only update rights if previously True
		for right in rights:
			if self.castling_rights[right]:
				self.castling_rights[right] = False
				move.updated_castling_rights.append(right)

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

	def undo_move(self):
		move = self.moves.pop()
		self.update_castling_rights(move, undo=True)

		if move.special_move == 'en_passant':
			self.undo_en_passant(move)
			return

		if move.special_move == 'castle':
			self.undo_castle(move)
			return

		move.piece.index = move.from_index
		self.board[move.from_index] = move.piece

		if move.captured_piece:
			move.captured_piece.index = move.to_index
			self.board[move.to_index] = move.captured_piece
			self.captured_pieces[move.captured_piece.color].remove(move.captured_piece)
		else:
			self.set_empty_square(move.to_index)

	def undo_en_passant(self, move):
		pass

	def undo_castle(self, move):
		pass

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
