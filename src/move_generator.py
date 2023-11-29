from move import Move


class MoveGenerator:
	BISHOP_DIRECTIONS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
	ROOK_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	KING_QUEEN_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS
	KNIGHT_DIRECTIONS = [
		(-2, -1), (-1, -2), (-2, 1), (-1, 2),
		(1, -2), (2, -1), (2, 1), (1, 2)
	]

	def __init__(self):
		pass

	# MOVE GENERATION

	def generate_pseudo_legal_moves(self, board, piece_list, castling_rights, prev_move=None):
		moves = {}

		for piece in piece_list:
			if piece.type == 'p':
				moves[piece.index] = self.generate_pawn_moves(
					piece,
					board,
					prev_move
				)
			elif piece.type == 'b':
				moves[piece.index] = self.generate_sliding_moves(
					piece,
					board,
					MoveGenerator.BISHOP_DIRECTIONS
				)
			elif piece.type == 'n':
				moves[piece.index] = self.generate_one_step_moves(
					piece,
					board,
					MoveGenerator.KNIGHT_DIRECTIONS
				)
			elif piece.type == 'r':
				moves[piece.index] = self.generate_sliding_moves(
					piece,
					board,
					MoveGenerator.ROOK_DIRECTIONS
				)
			elif piece.type == 'q':
				moves[piece.index] = self.generate_sliding_moves(
					piece,
					board,
					MoveGenerator.KING_QUEEN_DIRECTIONS
				)
			elif piece.type == 'k':
				normal_moves = self.generate_one_step_moves(
					piece,
					board,
					MoveGenerator.KING_QUEEN_DIRECTIONS
				)

				castling_moves = self.generate_castling_moves(
					piece,
					board,
					castling_rights
				)

				moves[piece.index] = normal_moves + castling_moves

		return moves

	def generate_pawn_moves(self, piece, board, prev_move):
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

		# check if pawn can move 1 square north
		north_index = row_north * 8 + col
		m = Move(piece.index, north_index, piece)
		if self.in_bounds(m, 0) and board[north_index].is_empty():
			moves.append(m)

			# check if pawn can move two squares north
			north_north_index = row_north_north * 8 + col
			m = Move(piece.index, north_north_index, piece)
			if self.in_bounds(m, 0) and board[north_north_index].is_empty():
				starting_rank = 6 if is_white else 1
				if is_white and row == starting_rank:
					moves.append(m)
				elif is_black and row == starting_rank:
					moves.append(m)

		# check if pawn can take northwest
		northwest_index = row_north * 8 + col_west
		m = Move(piece.index, northwest_index, piece)
		if (self.in_bounds(m, west_direction) and
				piece.diff_colors(board[northwest_index])):
			m.captured_piece = board[northwest_index]
			moves.append(m)

		# check if pawn can take northeast
		northeast_index = row_north * 8 + col_east
		m = Move(piece.index, northeast_index, piece)
		if (self.in_bounds(m, east_direction) and
				piece.diff_colors(board[northeast_index])):
			m.captured_piece = board[northeast_index]
			moves.append(m)

		# en passant
		if prev_move:
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
					m = Move(piece.index, to_index, piece, board[captured_piece_index], 
						special_move='en_passant')
					moves.append(m)

		return moves

	def generate_one_step_moves(self, piece, board, directions):
		moves = []

		for row_direction, col_direction in directions:
			cur_index = piece.index
			move_index = cur_index + row_direction * 8 + col_direction
			m = Move(cur_index, move_index, piece)
			if self.is_pseudo_legal_move(m, col_direction, board):
				if not board[move_index].is_empty():
					m.captured_piece = board[move_index]

				moves.append(m)

		return moves

	def generate_sliding_moves(self, piece, board, directions):
		moves = []

		for row_direction, col_direction in directions:
			cur_index = piece.index
			move_index = cur_index + row_direction * 8 + col_direction
			m = Move(cur_index, move_index, piece)

			while self.is_pseudo_legal_move(m, col_direction, board):
				# reset from_index to original index 
				m.from_index = piece.index
				moves.append(m)

				# if capture, then break (blocks ray)
				if piece.diff_colors(board[m.to_index]):
					m.captured_piece = board[m.to_index]
					break

				# increment in respective direction
				cur_index = move_index
				move_index += row_direction * 8 + col_direction
				m = Move(cur_index, move_index, piece)

		return moves

	def generate_castling_moves(self, piece, board, castling_rights):

		def empty_squares(squares):
			for piece in squares:
				if not piece.is_empty():
					return False

			return True

		moves = []

		if piece.is_black():
			# top left black rook
			if castling_rights['b_long']:
				in_between = board[1:4]
				if empty_squares(in_between):
					m = Move(4, 0, piece, special_move='castle')
					moves.append(m)

			# top right black rook
			if castling_rights['b_short']:
				in_between = board[5:7]
				if empty_squares(in_between):
					m = Move(4, 7, piece, special_move='castle')
					moves.append(m)

		else:
			# bottom left white rook
			if castling_rights['w_long']:
				in_between = board[57:60]
				if empty_squares(in_between):
					m = Move(60, 56, piece, special_move='castle')
					moves.append(m)

			# bottom right white rook
			if castling_rights['w_short']:
				in_between = board[61:63]
				if empty_squares(in_between):
					m = Move(60, 63, piece, special_move='castle')
					moves.append(m)

		return moves

	def in_check(self, king, board):
		king_row, king_col = king.index // 8, king.index % 8

		# straight rays
		for row_direction, col_direction in MoveGenerator.ROOK_DIRECTIONS:
			prev_index = king.index
			ray_index = king.index + row_direction * 8 + col_direction
			ray_move = Move(prev_index, ray_index, None)

			while self.in_bounds(ray_move, col_direction):
				piece = board[ray_index]

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
		for row_direction, col_direction in MoveGenerator.BISHOP_DIRECTIONS:
			prev_index = king.index
			ray_index = king.index + row_direction * 8 + col_direction
			ray_move = Move(prev_index, ray_index, None)

			while self.in_bounds(ray_move, col_direction):
				piece = board[ray_index]

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
			ne_piece = board[northeast]
			if ne_piece.diff_colors(king) and ne_piece.type == 'p':
				return True

		if self.in_bounds(nw_ray_move, west):
			nw_piece = board[northwest]
			if nw_piece.diff_colors(king) and nw_piece.type == 'p':
				return True

		# knight
		for row_direction, col_direction in MoveGenerator.KNIGHT_DIRECTIONS:
			ray_index = king.index + row_direction * 8 + col_direction
			ray_move = Move(king.index, ray_index, None)

			if self.in_bounds(ray_move, col_direction):
				piece = board[ray_index]
				if piece.diff_colors(king) and piece.type == 'n':
					return True

		# enemy king
		for row_direction, col_direction in MoveGenerator.KING_QUEEN_DIRECTIONS:
			ray_index = king.index + row_direction * 8 + col_direction
			ray_move = Move(king.index, ray_index, None)

			if self.in_bounds(ray_move, col_direction):
				piece = board[ray_index]
				if piece.diff_colors(king) and piece.type == 'k':
					return True

		return False

	# HELPER FUNCTIONS

	def is_pseudo_legal_move(self, move, horiz_direction, board):
		if self.in_bounds(move, horiz_direction):
			from_piece = move.piece
			to_piece = board[move.to_index]
			return from_piece.diff_colors_or_empty(to_piece)

		return False

	def in_bounds(self, move, horiz_direction):
		in_vertical_bounds = (0 <= move.to_index <= 63)

		# check for wrapping
		from_col = move.from_index % 8
		to_col = move.to_index % 8
		in_horizontal_bounds = (to_col == (from_col + horiz_direction))

		return in_vertical_bounds and in_horizontal_bounds
