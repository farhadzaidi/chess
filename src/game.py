import pygame
from board import Board

pygame.init()

SCREEN_WIDTH = 680
SCREEN_HEIGHT = 600
SQ_DIM = 63
BOARD_DIM = SQ_DIM * 8
PADDING = 50
FONT_SIZE = 20

LIGHT = '#F5F5F5'
DARK = '#2E2E38'
INFO = '#7FD4F5'
DANGER = '#F06070'

pygame.display.set_caption('Chess')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont('comicsansms', FONT_SIZE)

def draw_board():
	# draw border
	border = (PADDING, PADDING, BOARD_DIM, BOARD_DIM)
	pygame.draw.rect(screen, DARK, border, 3)

	# ranks and files
	for i in range(1, 9):
		rank = (18, PADDING + SQ_DIM * (8 - i) + 15)
		screen.blit(font.render(f'{i}', True, 'black'), rank)

		file = (PADDING + SQ_DIM * (i - 1) + 25, PADDING + BOARD_DIM + 5)
		screen.blit(font.render(f'{chr(i + 96)}', True, 'black'), file)

	# checkerboard pattern
	for row in range(8):
		for col in range(4):
			sq_x = PADDING + 2 * SQ_DIM * col
			sq_y = PADDING + SQ_DIM * row

			# apply x-offset to even rows
			if row % 2 == 0:
				sq_x += SQ_DIM

			square = (sq_x, sq_y, SQ_DIM, SQ_DIM)
			pygame.draw.rect(screen, DARK, square)


def draw_pieces():
	for piece in b.board:
		if piece.is_empty():
			continue

		row, col = piece.index // 8, piece.index % 8
		p_x = PADDING + col * SQ_DIM
		p_y = PADDING + row * SQ_DIM
		screen.blit(piece_images[piece.symbol][0], (p_x, p_y))

		# selected
		if piece.index == selected or piece.index == selected_other_side:
			outline = (p_x, p_y, SQ_DIM, SQ_DIM)
			pygame.draw.rect(screen, INFO, outline, 3)


def draw_moves(from_index, valid_moves):
	for move in valid_moves.get(from_index, []):
		row, col = move.to_index // 8, move.to_index % 8
		sq_x = PADDING + col * SQ_DIM
		sq_y = PADDING + row * SQ_DIM
		center = (sq_x + SQ_DIM // 2, sq_y + SQ_DIM // 2)
		radius = 7
		pygame.draw.circle(screen, INFO, center, radius)


def draw_captured_pieces():
	for color in b.captured_pieces:
		for i, piece in enumerate(sorted(b.captured_pieces[color])):
			p_x = PADDING + BOARD_DIM + 20
			p_y = PADDING + 30 * i

			if color == 'b':
				p_x += 40

			screen.blit(piece_images[piece.symbol][1], (p_x, p_y))


def draw_check():
	for color in b.checks:
		if b.checks[color]:
			king_index = b.king_index[color]
			row, col = king_index // 8, king_index % 8
			p_x = PADDING + col * SQ_DIM
			p_y = PADDING + row * SQ_DIM
			outline = (p_x, p_y, SQ_DIM, SQ_DIM)
			pygame.draw.rect(screen, DANGER, outline, 3)


b = Board()

# load piece images
piece_images = {}
for piece in b.board:
	if piece.is_empty():
		continue

	path = f'../images/{piece.symbol}.png'
	img = pygame.image.load(path)
	img_normal = pygame.transform.smoothscale(img, (SQ_DIM, SQ_DIM))
	img_sm = pygame.transform.smoothscale(img, (30, 30))

	piece_images[piece.symbol] = (img_normal, img_sm)


turn = 'w'
valid_moves = b.get_valid_moves(turn)

timer = pygame.time.Clock()
fps = 60
run = True
selected = None
selected_other_side = None
while run:
	timer.tick(fps)
	screen.fill(LIGHT)

	draw_board()
	draw_pieces()
	draw_captured_pieces()
	draw_check()

	if not valid_moves:
		if turn == 'w' and b.checks['w']:
			game_end_text = 'CHECKMATE! BLACK WINS!'
		elif turn == 'b' and b.checks['b']:
			game_end_text = 'CHECKMATE! WHITE WINS!'
		else:
			game_end_text = "STALEMATE! IT'S A DRAW!"

		screen.blit(font.render(game_end_text, True, 'black'), (180, 15))

	if selected is not None:
		draw_moves(selected, valid_moves)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			col = (event.pos[0] - PADDING) // SQ_DIM
			row = (event.pos[1] - PADDING) // SQ_DIM

			if 0 <= row <= 7 and 0 <= col <= 7:
				if selected is None:
					from_index = int(row * 8 + col)
					if b.board[from_index].color == turn:
						selected = from_index
						selected_other_side = None
					elif not b.board[from_index].is_empty():
						if from_index == selected_other_side:
							selected_other_side = None
						else:
							selected_other_side = from_index
					else:
						selected_other_side = from_index
				else:
					to_index = int(row * 8 + col)
					is_valid_move = False
					for move in valid_moves.get(from_index, []):
						if to_index == move.to_index:
							is_valid_move = True
							b.make_move(move)
							turn = 'w' if turn == 'b' else 'b'
							valid_moves = b.get_valid_moves(turn)
							selected = None

					if not is_valid_move:
						if from_index == to_index:
							selected = None
						elif b.board[from_index].same_colors(b.board[to_index]):
							selected = to_index
							from_index = to_index 
						elif not b.board[to_index].is_empty():
							selected_other_side = to_index
							selected = None
						else:
							selected = None

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				if b.moves:
					b.undo_move()
					turn = 'w' if turn == 'b' else 'b'
					valid_moves = b.get_valid_moves(turn)
					selected = None
					selected_other_side = None

	pygame.display.flip()

pygame.quit()