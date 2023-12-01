from piece import Piece
from move import Move


class Board:
	BISHOP_DIRECTIONS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
	ROOK_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	KING_QUEEN_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS
	KNIGHT_DIRECTIONS = [
    	(-2, -1), (-1, -2), (-2, 1), (-1, 2),
    	(1, -2), (2, -1), (2, 1), (1, 2)
	]


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


##############################
# MAKE AND UNDO MOVE METHODS #
##############################


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

			if move.special_move == 'promotion':
				self.board[move.to_index].type = 'q'
				self.board[move.to_index].symbol = 'wq'

		self.update_checks()


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

			if move.special_move == 'promotion':
				move.piece.type = 'p'
				move.piece.symbol = 'wp'

		# undo king index 
		# works regardless of whether or not the previous move was a castle
		if move.piece.type == 'k':
			self.king_index[move.piece.color] = move.from_index

		self.update_checks()


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


###########################
# MOVE GENERATION METHODS #
###########################


	def get_valid_moves(self, side):

		def is_valid_move(move, side):
			is_valid = False

			self.make_move(move)
			if not self.in_check(side):
				is_valid = True
			self.undo_move()

			return is_valid

		valid_moves = {}
		moves = self.generate_pseudo_legal_moves(side)

		for from_index, move_list in moves.items():
			if not move_list:
				continue

			valid_move_list = []
			for move in move_list:
				if move.special_move == 'castle':
					# make sure king isn't in check and doesn't end up in check after castling
					king_in_check = self.in_check(side)
					king_in_check_after_castling = not is_valid_move(move, side)

					if not king_in_check and not king_in_check_after_castling:

						# king can't castle if path is attacked
						if move.to_index == 7 or move.to_index == 63:
							king_index = self.king_index[move.piece.color]
							king = self.board[king_index]
							m = Move(king_index, king_index + 1, king)
							if is_valid_move(m, side):
								valid_move_list.append(move)

						elif move.to_index == 0 or move.to_index == 56:
							king_index = self.king_index[move.piece.color]
							king = self.board[king_index]
							m = Move(king_index, king_index - 1, king)
							if is_valid_move(m, side):
								valid_move_list.append(move)

				elif is_valid_move(move, side):
					valid_move_list.append(move)

			if valid_move_list:
				valid_moves[from_index] = valid_move_list

		return valid_moves


	def generate_pseudo_legal_moves(self, side):
		moves = {}

		for piece in self.pieces[side]:
			if piece.type == 'p':
				moves[piece.index] = self.generate_pawn_moves(piece)
			elif piece.type == 'b':
				moves[piece.index] = self.generate_sliding_moves(piece, Board.BISHOP_DIRECTIONS)
			elif piece.type == 'n':
				moves[piece.index] = self.generate_one_step_moves(piece, Board.KNIGHT_DIRECTIONS)
			elif piece.type == 'r':
				moves[piece.index] = self.generate_sliding_moves(piece, Board.ROOK_DIRECTIONS)
			elif piece.type == 'q':
				moves[piece.index] = self.generate_sliding_moves(piece, Board.KING_QUEEN_DIRECTIONS)
			elif piece.type == 'k':
				normal_moves = self.generate_one_step_moves(piece, Board.KING_QUEEN_DIRECTIONS)
				castling_moves = self.generate_castling_moves(piece)
				moves[piece.index] = normal_moves + castling_moves

		return moves


	def generate_pawn_moves(self, piece):
		moves = []
		row, col = piece.index // 8, piece.index % 8
		is_white = piece.is_white()
		is_black = piece.is_black()

		# TODO: implement promotions - pawn can never be on last rank
		if (is_white and row == 0) or (is_black and row == 7):
			return moves

		# set directions based on pawn perspective
		north_direction = -1 if is_white else 1
		east_direction = 1 if is_white else -1
		west_direction = -1 if is_white else 1

		row_north = row + north_direction
		row_north_north = row_north + north_direction
		col_east = col + east_direction
		col_west = col + west_direction

		last_rank = 0 if is_white else 7

		# check if pawn can move 1 square north
		north_index = row_north * 8 + col
		m = Move(piece.index, north_index, piece)
		if self.in_bounds(m, 0) and self.board[north_index].is_empty():
			if row_north == last_rank:
				m.special_move = 'promotion'
			moves.append(m)

			# check if pawn can move two squares north
			north_north_index = row_north_north * 8 + col
			m = Move(piece.index, north_north_index, piece)
			if self.in_bounds(m, 0) and self.board[north_north_index].is_empty():
				starting_rank = 6 if is_white else 1
				if is_white and row == starting_rank:
					moves.append(m)
				elif is_black and row == starting_rank:
					moves.append(m)

		# check if pawn can take northwest
		northwest_index = row_north * 8 + col_west
		m = Move(piece.index, northwest_index, piece)
		if (self.in_bounds(m, west_direction) and
				piece.diff_colors(self.board[northwest_index])):
			m.captured_piece = self.board[northwest_index]
			if row_north == last_rank:
				m.special_move = 'promotion'
			moves.append(m)

		# check if pawn can take northeast
		northeast_index = row_north * 8 + col_east
		m = Move(piece.index, northeast_index, piece)
		if (self.in_bounds(m, east_direction) and
				piece.diff_colors(self.board[northeast_index])):
			m.captured_piece = self.board[northeast_index]
			if row_north == last_rank:
				m.special_move = 'promotion'
			moves.append(m)

		# en passant
		if moves:
			prev_move = moves[-1]
			prev_move_from_row = prev_move.from_index // 8
			prev_move_to_row = prev_move.to_index // 8
			prev_move_to_col = prev_move.to_index % 8

			move_two_squares = abs(prev_move_to_row - prev_move_from_row) == 2
			if (prev_move.piece.type == 'p' and piece.diff_colors(prev_move.piece) and 
					move_two_squares):
				to_index = None

				# take northwest
				if row == prev_move_to_row and col_west == prev_move_to_col:
					to_index = northwest_index
				# take northeast
				elif row == prev_move_to_row and col_east == prev_move_to_col:
					to_index = northeast_index

				# can take en passant
				if to_index:
					captured_piece_index = to_index + 8 if is_white else to_index - 8
					m = Move(piece.index, to_index, piece, self.board[captured_piece_index], 
						special_move='en_passant')
					moves.append(m)

		return moves


	def generate_one_step_moves(self, piece, directions):
		moves = []

		for row_direction, col_direction in directions:
			cur_index = piece.index
			move_index = cur_index + row_direction * 8 + col_direction
			m = Move(cur_index, move_index, piece)
			if self.is_pseudo_legal_move(m, col_direction):
				if not self.board[move_index].is_empty():
					m.captured_piece = self.board[move_index]

				moves.append(m)

		return moves


	def generate_sliding_moves(self, piece, directions):
		moves = []

		for row_direction, col_direction in directions:
			cur_index = piece.index
			move_index = cur_index + row_direction * 8 + col_direction
			m = Move(cur_index, move_index, piece)

			while self.is_pseudo_legal_move(m, col_direction):
				# reset from_index to original index 
				m.from_index = piece.index
				moves.append(m)

				# if capture, then break (blocks ray)
				if piece.diff_colors(self.board[m.to_index]):
					m.captured_piece = self.board[m.to_index]
					break

				# increment in respective direction
				cur_index = move_index
				move_index += row_direction * 8 + col_direction
				m = Move(cur_index, move_index, piece)


		return moves


	def generate_castling_moves(self, piece):

		def empty_squares(squares):
			for piece in squares:
				if not piece.is_empty():
					return False

			return True

		moves = []

		if piece.is_black():
			# top left black rook
			if self.castling_rights['b_long']:
				in_between = self.board[1:4]
				if empty_squares(in_between):
					m = Move(4, 0, piece, special_move='castle')
					moves.append(m)

			# top right black rook
			if self.castling_rights['b_short']:
				in_between = self.board[5:7]
				if empty_squares(in_between):
					m = Move(4, 7, piece, special_move='castle')
					moves.append(m)

		else:
			# bottom left white rook
			if self.castling_rights['w_long']:
				in_between = self.board[57:60]
				if empty_squares(in_between):
					m = Move(60, 56, piece, special_move='castle')
					moves.append(m)

			# bottom right white rook
			if self.castling_rights['w_short']:
				in_between = self.board[61:63]
				if empty_squares(in_between):
					m = Move(60, 63, piece, special_move='castle')
					moves.append(m)

		return moves


#######################
# BOARD STATE METHODS #
#######################


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
		self.checks['w'] = self.in_check('w')
		self.checks['b'] = self.in_check('b')


	def in_check(self, side):
		king = self.board[self.king_index[side]]
		king_row, king_col = king.index // 8, king.index % 8

		# straight rays
		for row_direction, col_direction in Board.ROOK_DIRECTIONS:
			prev_index = king.index
			ray_index = king.index + row_direction * 8 + col_direction
			ray_move = Move(prev_index, ray_index, None)

			while self.in_bounds(ray_move, col_direction):
				piece = self.board[ray_index]

				# break if the ray runs into a piece
				# return True if the king is attacked
				if not piece.is_empty():
					if piece.diff_colors(king) and piece.type in 'rq':
						return True
					break

				# increment
				prev_index = ray_index
				ray_index += row_direction * 8 + col_direction
				ray_move = Move(prev_index, ray_index, None)

		# diagnal rays
		for row_direction, col_direction in Board.BISHOP_DIRECTIONS:
			prev_index = king.index
			ray_index = king.index + row_direction * 8 + col_direction
			ray_move = Move(prev_index, ray_index, None)

			while self.in_bounds(ray_move, col_direction):
				piece = self.board[ray_index]

				# break if the ray runs into a piece
				# return True if the king is attacked
				if not piece.is_empty():
					if piece.diff_colors(king) and piece.type in 'bq':
						return True
					break

				# increment
				prev_index = ray_index
				ray_index += row_direction * 8 + col_direction
				ray_move = Move(prev_index, ray_index, None)

		# pawn
		if king.color == 'w':
			east, west = 1, -1
			northeast = king.index - 7
			northwest = king.index - 9
		else:
			east, west = -1, 1
			northeast = king.index + 7
			northwest = king.index + 9

		ne_ray_move = Move(king.index, northeast, None)
		nw_ray_move = Move(king.index, northwest, None)

		if self.in_bounds(ne_ray_move, east):
			ne_piece = self.board[northeast]
			if ne_piece.diff_colors(king) and ne_piece.type == 'p':
				return True

		if self.in_bounds(nw_ray_move, west):
			nw_piece = self.board[northwest]
			if nw_piece.diff_colors(king) and nw_piece.type == 'p':
				return True

		# knight
		for row_direction, col_direction in Board.KNIGHT_DIRECTIONS:
			ray_index = king.index + row_direction * 8 + col_direction
			ray_move = Move(king.index, ray_index, None)

			if self.in_bounds(ray_move, col_direction):
				piece = self.board[ray_index]
				if piece.diff_colors(king) and piece.type == 'n':
					return True

		# enemy king
		for row_direction, col_direction in Board.KING_QUEEN_DIRECTIONS:
			ray_index = king.index + row_direction * 8 + col_direction
			ray_move = Move(king.index, ray_index, None)

			if self.in_bounds(ray_move, col_direction):
				piece = self.board[ray_index]
				if piece.diff_colors(king) and piece.type == 'k':
					return True

		return False


##################
# HELPER METHODS #
##################


	def set_empty_square(self, index):
		self.board[index] = Piece('0', '0', index, '00')


	def in_bounds(self, move, horiz_direction):
		in_vertical_bounds = (0 <= move.to_index <= 63)

		# check for wrapping
		from_col = move.from_index % 8
		to_col = move.to_index % 8
		in_horizontal_bounds = (to_col == (from_col + horiz_direction))

		return in_vertical_bounds and in_horizontal_bounds


	def is_pseudo_legal_move(self, move, horiz_direction):
		if self.in_bounds(move, horiz_direction):
			from_piece = move.piece
			to_piece = self.board[move.to_index]
			return from_piece.diff_colors_or_empty(to_piece)

		return False


	def __repr__(self):
		s = '\n'
		for row in range(8):
			s += f'\n\t{row + 1} | '
			for col in range(8):
				index = row * 8 + col
				s += f'{self.board[index].symbol} '

		s += '\n\t    a  b  c  d  e  f  g  h\n'

		return s
