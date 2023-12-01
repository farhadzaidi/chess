#########################################
# ---- used for testing move generation ----
# perft function makes moves and unmakes every possible
# move in a given position and counts the number of possible
# moves at a given depth 
	# depth = 1 --> first move (white
	# depth = 2 --> second move (black)
	# depth = 3 --> third move (white)
	# ...
# the number of moves is compared to a consensus of perft values
# among chess programmers
#########################################

from board import Board

def perft(depth, b, turn='w'):
	if depth == 0:
		return 1

	valid_moves = b.get_valid_moves(turn)
	nodes = 0
	for move, move_list in valid_moves.items():
		for move in move_list:
			b.make_move(move)
			nodes += perft(depth - 1, b, turn = 'w' if turn == 'b' else 'b')
			b.undo_move()

	return nodes


b = Board()
depth = 4
nodes = perft(depth, b)
print(f'{nodes} nodes generated at depth {depth}')
