from piece import Piece
from move import Move
from move_generator import MoveGenerator


class Board:
	move_generator = MoveGenerator()

	def __init__(self):
		self.initialize_board_and_pieces()
		self.moves = []
		self.undone_moves = []
		self.captured_pieces = {'w': [], 'b': []}
		self.king_index = {'w': 60, 'b': 4}
		self.checks = {'w': False, 'b': False}
		self.castling_rights = {
			'w_short': True,
			'w_long': True,
			'b_short': True,
			'b_long': True
		}


	def initialize_board_and_pieces(self):
		self.pieces = {'w': [], 'b': []}
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
			piece = Piece(piece[0], piece[1], i, piece)
			self.board[i] = piece
			if not piece.is_empty():
				self.pieces[piece.color].append(piece)


	def make_move(self, move):
		self.moves.append(move)
		self.update_castling_rights(move)

		if move.special_move == 'castle':
			self.castle(move)
		else:
			move.piece.index = move.to_index
			self.board[move.to_index] = move.piece
			self.set_empty_square(move.from_index)

			# update capture
			if move.captured_piece:
				self.captured_pieces[move.captured_piece.color].append(move.captured_piece)
				self.pieces[move.captured_piece.color].remove(move.captured_piece)

				if move.special_move == 'en_passant':
					self.set_empty_square(move.captured_piece.index)

			# update king index
			# handled separately in castle method
			if move.piece.type == 'k':
				self.king_index[move.piece.color] = move.to_index

		self.update_checks()


	def undo_move(self):
		move = self.moves.pop()
		self.update_castling_rights(move, undo=True)

		if move.special_move == 'castle':
			self.undo_castle(move)
		else:
			move.piece.index = move.from_index
			self.board[move.from_index] = move.piece

			# undo capture
			if move.captured_piece:
				self.board[move.captured_piece.index] = move.captured_piece
				self.captured_pieces[move.captured_piece.color].remove(move.captured_piece)
				self.pieces[move.captured_piece.color].append(move.captured_piece)

				if move.special_move == 'en_passant':
					self.set_empty_square(move.to_index)
			else:
				self.set_empty_square(move.to_index)

			# undo king index 
			# works regardless of whether or not the previous move was a castle
			if move.piece.type == 'k':
				self.king_index[move.piece.color] = move.from_index

		self.update_checks()


	def get_valid_moves(self, turn):

		def is_valid_move(move, king):
			is_valid = False

			self.make_move(move)
			if not Board.move_generator.in_check(king, self.board):
				is_valid = True
			else:
				print(f'invalid_move: {move}')
			self.undo_move()

			return is_valid

		king = self.board[self.king_index[turn]]
		valid_moves = {}
		moves = Board.move_generator.generate_pseudo_legal_moves(
			self.board,
			self.pieces[turn],
			self.castling_rights,
			self.moves[-1] if self.moves else None
		)

		for from_index, move_list in moves.items():
			if not move_list:
				continue

			valid_move_list = []
			for move in move_list:
				if is_valid_move(move, king):
					valid_move_list.append(move)

			if valid_move_list:
				valid_moves[from_index] = valid_move_list

		return valid_moves
		# return moves


	def update_castling_rights(self, move, undo=False):
		if undo:
			if move.updated_castling_rights:
				for right in move.updated_castling_rights:
					self.castling_rights[right] = True
				move.updated_castling_rights = []
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

		# only set castling rights to False if they were previously True
		for right in rights:
			if self.castling_rights[right]:
				self.castling_rights[right] = False
				move.updated_castling_rights.append(right)


	def update_checks(self):
		white_king = self.board[self.king_index['w']]
		self.checks['w'] = Board.move_generator.in_check(white_king, self.board)
		black_king = self.board[self.king_index['b']]
		self.checks['b'] = Board.move_generator.in_check(black_king, self.board)


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

		# update king index
		self.king_index[king.color] = king_pos


	def undo_castle(self, move):
		# long castle
		if move.to_index == 0 or move.to_index == 56:
			in_between = range(move.to_index + 1, move.from_index)
			rook_pos = move.to_index + 3
		# short castle
		else:
			in_between = range(move.from_index + 1, move.to_index)
			rook_pos = move.to_index - 2

		# update king pos
		move.piece.index = move.from_index
		self.board[move.from_index] = move.piece

		# update rook pos
		rook = self.board[rook_pos]
		rook.index = move.to_index
		self.board[move.to_index] = rook

		# set empty squares in between
		for index in in_between:
			self.set_empty_square(index)


	def set_empty_square(self, index):
		self.board[index] = Piece('0', '0', index, '00')

	def __repr__(self):
		s = '\n'
		for row in range(8):
			s += f'\n\t{row + 1} | '
			for col in range(8):
				index = row * 8 + col
				s += f'{self.board[index].symbol} '

		s += '\n\t    a  b  c  d  e  f  g  h\n'

		return s
