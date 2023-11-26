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

	def generate_pseudo_legal_moves(self, board, castling_rights, prev_move=None):
		moves = {}

		for piece in board:
			if piece.type == 'p':
				moves[piece.index] = self.generate_pawn_moves(piece, board, 
					prev_move)
			elif piece.type == 'b':
				moves[piece.index] = self.generate_sliding_moves(piece, board,
					MoveGenerator.BISHOP_DIRECTIONS)
			elif piece.type == 'n':
				moves[piece.index] = self.generate_one_step_moves(piece, board,
					MoveGenerator.KNIGHT_DIRECTIONS)
			elif piece.type == 'r':
				moves[piece.index] = self.generate_sliding_moves(piece, board, 
					MoveGenerator.ROOK_DIRECTIONS)
			elif piece.type == 'q':
				moves[piece.index] = self.generate_sliding_moves(piece, board, 
					MoveGenerator.KING_QUEEN_DIRECTIONS)
			elif piece.type == 'k':
				normal_moves = self.generate_one_step_moves(piece, board, 
					MoveGenerator.KING_QUEEN_DIRECTIONS)
				castling_moves = self.generate_castling_moves(piece, board, 
					castling_rights)
				moves[piece.index] = normal_moves.union(castling_moves)

		return moves

	def generate_pawn_moves(self, piece, board, prev_move):
		moves = set()
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

		# check if pawn can move 1 square north
		row_north = row + north_direction
		north_index = row_north * 8 + col
		if board[north_index].is_empty():
			moves.add(north_index)

			# check if pawn can move two squares north
			north_north_index = (row_north + north_direction) * 8 + col
			if board[north_north_index].is_empty():
				starting_rank = 6 if is_white else 1
				if is_white and row == starting_rank:
					moves.add(north_north_index)
				elif is_black and row == starting_rank:
					moves.add(north_north_index)

		# check if pawn can take northwest
		northwest_index = row_north * 8 + (col + west_direction)
		move_northwest = Move(piece.index, northwest_index, piece)
		in_bounds = self.in_bounds(move_northwest, west_direction)
		if in_bounds and piece.diff_colors(board[northwest_index]):
			moves.add(northwest_index)

		# check if pawn can take northeast
		northeast_index = row_north * 8 + (col + east_direction)
		move_northeast = Move(piece.index, northeast_index, piece)
		in_bounds = self.in_bounds(move_northeast, east_direction)
		if in_bounds and piece.diff_colors(board[northeast_index]):
			moves.add(northeast_index)

		# en passant
		if prev_move:
			from_piece = prev_move.piece
			from_row = prev_move.from_index // 8
			to_row = prev_move.to_index // 8
			to_col = prev_move.to_index % 8

			move_two_squares = abs(to_row - from_row) == 2
			if (from_piece.type == 'p' and piece.diff_colors(from_piece) 
				and move_two_squares):

				# take northwest
				if row == to_row and (col + west_direction) == to_col:
					moves.add(northwest_index)

				# take northeast
				if row == to_row and (col + east_direction) == to_col:
					moves.add(northeast_index)

		return moves

	def generate_one_step_moves(self, piece, board, directions):
		moves = set()

		for row_direction, col_direction in directions:
			cur_index = piece.index
			move_index = cur_index + row_direction * 8 + col_direction
			move = Move(cur_index, move_index, piece)
			if self.is_pseudo_legal_move(move, col_direction, board):
				moves.add(move_index)

		return moves

	def generate_sliding_moves(self, piece, board, directions):
		moves = set()

		for row_direction, col_direction in directions:
			cur_index = piece.index
			move_index = cur_index + row_direction * 8 + col_direction
			move = Move(cur_index, move_index, piece)

			while self.is_pseudo_legal_move(move, col_direction, board):
				moves.add(move.to_index)

				# if capture, then break (blocks ray)
				if piece.diff_colors(board[move.to_index]):
					break

				# increment in respective direction
				move.from_index = move.to_index
				move.to_index += row_direction * 8 + col_direction

		return moves

	def generate_castling_moves(self, piece, board, castling_rights):

		def empty_squares(squares):
			for piece in squares:
				if not piece.is_empty():
					return False

			return True

		moves = set()

		if piece.is_black():
			# top left black rook
			if castling_rights['black_long']:
				in_between = board[1:4]
				if empty_squares(in_between):
					moves.add(0)

			# top right black rook
			if castling_rights['black_short']:
				in_between = board[5:7]
				if empty_squares(in_between):
					moves.add(7)

		else:
			# bottom left white rook
			if castling_rights['white_long']:
				in_between = board[57:60]
				if empty_squares(in_between):
					moves.add(56)

			# bottom right white rook
			if castling_rights['white_short']:
				in_between = board[61:63]
				if empty_squares(in_between):
					moves.add(63)

		return moves

	# HELPER FUNCTIONS

	def is_pseudo_legal_move(self, move, horiz_direction, board):
		if self.in_bounds(move, horiz_direction):
			from_piece = move.piece
			to_piece = board[move.to_index]
			return from_piece.diff_colors_or_empty(to_piece)
		else:
			return False

	def in_bounds(self, move, horiz_direction):
		in_vertical_bounds = (0 <= move.to_index <= 63)

		# check for wrapping
		from_col = move.from_index % 8
		to_col = move.to_index % 8
		in_horizontal_bounds = (to_col == (from_col + horiz_direction))

		return in_vertical_bounds and in_horizontal_bounds


