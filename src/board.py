class Board:	
	def __init__(self):
		self.board = [
			'r', 'n', 'b', 'q', 'k', 'b', 'n', 'r',
			'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p',
			'+', '+', '+', '+', '+', '+', '+', '+',
			'+', '+', '+', '+', '+', '+', '+', '+',
			'+', '+', '+', '+', '+', '+', '+', '+',
			'+', '+', '+', '+', '+', '+', '+', '+',
			'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
			'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R',
		]

		self.black_pieces = self.board[0:16]
		self.white_pieces = self.board[48:64]

		self.moves = []
		self.valid_moves = self.move_gen(self.board)

	# HELPER FUNCTIONS

	# returns True if and only is piece is white
	@staticmethod
	def is_white(p):
		return p != '+' and p.isupper()

	# returns True if and only if piece is black
	@staticmethod
	def is_black(p):
		return p != '+' and p.islower()

	# returns True if and only if the pieces are opposite colors
	# unless empty=True, then returns True if either square is empty
	@staticmethod
	def opp_colors(p1, p2, empty=False):
		if p1 == '+' or p2 == '+':
			return empty or False

		return Board.is_white(p1) ^ Board.is_white(p2)

	# returns True if and only if the pieces are same colors
	# unless empty=True, then returns True if either square is empty
	@staticmethod
	def same_colors(p1, p2, empty=False):
		if p1 == '+' or p2 == '+':
			return empty or False

		return not (Board.is_white(p1) ^ Board.is_white(p2))

	@staticmethod
	def in_bounds(idx):
		return 0 <= idx <= 63

	# given two subsequent moves and a column delta, returns 
	# True if the two moves are physically consistent on a 
	# chessboard (i.e. returns False if the second move wraps
	# around to the other side)
	@staticmethod
	def no_wrap(cur_idx, new_idx, delta):
		cur_col, new_col = cur_idx % 8, new_idx % 8
		return new_col == (cur_col + delta)

	# checks if the move is psuedo-legal 
	# i.e. does not account for checks
	@staticmethod
	def is_valid_move(cur_idx, new_idx, p, pos, delta):
		return (Board.in_bounds(new_idx) and 
			Board.no_wrap(cur_idx, new_idx, delta)
			and Board.opp_colors(p, pos[new_idx], empty=True))

	# CLASS METHODS

	def make_move(self, from_idx, to_idx, p_type):
		self.moves.append((from_idx, to_idx, p_type))

		from_piece = self.board[from_idx]
		to_piece = self.board[to_idx]

		# move piece
		self.board[from_idx] = '+'
		self.board[to_idx] = from_piece

		# remove from respective list
		if Board.is_white(to_piece):
			self.white_pieces.remove(to_piece)

		if Board.is_black(to_piece):
			self.black_pieces.remove(to_piece)

		# call move gen after every move to generate 
		# valid moves for next pos
		self.valid_moves = self.move_gen(self.board)

	def move_gen(self, pos):
		moves = {}
		bishop_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
		knight_directions = [(-2, -1), (-1, -2), (-2, 1), (-1, 2), 
			(1, -2), (2, -1), (2, 1), (1, 2)]
		rook_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
		king_queen_directions = bishop_directions + rook_directions

		for i, p in enumerate(pos):
			if p in 'pP':
				moves[i] = self.pawn_move_gen(i, p, pos)
			elif p in 'bB':
				moves[i] = self.sliding_move_gen(i, p, pos, bishop_directions)
			elif p in 'nN':
				moves[i] = self.king_knight_move_gen(i, p, pos, 
					knight_directions)
			elif p in 'rR':
				moves[i] = self.sliding_move_gen(i, p, pos, rook_directions)
			elif p in 'qQ':
				moves[i] = self.sliding_move_gen(i, p, pos, 
					king_queen_directions)
			elif p in 'kK':
				moves[i] = self.king_knight_move_gen(i, p, pos, 
					king_queen_directions)

		return moves

	def pawn_move_gen(self, i, p, pos):
		moves = set()
		row, col = i // 8, i % 8

		# TODO: implement promotions - pawn can never be on last rank
		if (Board.is_white(p) and row == 0
			or Board.is_black(p) and row == 7):
			return moves

		# set directions based on pawn perspective
		north_d = -1 if Board.is_white(p) else 1
		east_d = 1 if Board.is_white(p) else -1
		west_d = -1 if Board.is_white(p) else 1

		# check if pawn can move 1 square north
		row_north = row + north_d
		north = row_north * 8 + col
		if pos[north] == '+':
			moves.add(north)

			# check if pawn can move two squares north
			north_north = (row_north + north_d) * 8 + col
			if pos[north_north] == '+':
				if Board.is_white(p) and row == 6:
					moves.add(north_north)
				elif Board.is_black(p) and row == 1:
					moves.add(north_north)

		# check if pawn can take northwest
		northwest = row_north * 8 + (col + west_d)
		if (0 <= (col + west_d) <= 7) and Board.opp_colors(p, pos[northwest]):
			moves.add(northwest)

		# check if pawn can take northeast
		northeast = row_north * 8 + (col + east_d)
		if (0 <= (col + east_d) <= 7) and Board.opp_colors(p, pos[northeast]):
			moves.add(northeast)

		# en passant
		if self.moves:
			prev_move = self.moves[-1]
			from_row = prev_move[0] // 8
			to_row = prev_move[1] // 8
			to_col = prev_move[1] % 8
			p_type = prev_move[2]

			if (p_type in 'pP' and Board.opp_colors(p, p_type)
				and abs(from_row - to_row) == 2):

				# take northwest
				if row == to_row and (col + west_d) == to_col:
					moves.add(northwest)

				# take northeast
				if row == to_row and (col + east_d) == to_col:
					moves.add(northeast)

		return moves

	def king_knight_move_gen(self, i, p, pos, directions):
		moves = set()
		row, col = i // 8, i % 8

		for row_d, col_d in directions:
			new_idx = (row + row_d) * 8 + (col + col_d)
			if Board.is_valid_move(i, new_idx, p, pos, col_d):
				moves.add(new_idx)

		return moves

	def sliding_move_gen(self, i, p, pos, directions):
		moves = set()
		row, col = i // 8, i % 8

		for row_d, col_d in directions:
			cur_idx = i
			new_idx = (row + row_d) * 8 + (col + col_d)
			while Board.is_valid_move(cur_idx, new_idx, p, pos, col_d):
				# valid move
				moves.add(new_idx)

				# if capture, then break (blocks ray)
				if Board.opp_colors(p, pos[new_idx]):
					break

				# increment in respective direction
				cur_idx = new_idx
				new_idx += row_d * 8 + col_d

		return moves

	def __repr__(self):
		s = '\n'
		for rank in range(8):
			# print rank numbers
			s += f'{rank + 1}| '
			for file in range(8):
				idx = rank * 8 + file
				s += f'{self.board[idx]} '

			s += '\n'

		# print file letters
		s += '   ---------------\n'
		s += '   a b c d e f g h'
		return s
		