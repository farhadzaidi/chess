import pygame
from board import Board

pygame.init()

# the GUI and all of its assets are scaled with 
# the user's screen size
SCREEN_WIDTH = pygame.display.Info().current_w // 1.6
SCREEN_HEIGHT = pygame.display.Info().current_h // 1.15
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 600
SQ_DIM = SCREEN_HEIGHT // 9.5
BOARD_DIM = SQ_DIM * 8
PADDING = (SCREEN_HEIGHT - BOARD_DIM) // 2

LIGHT = '#F5F5F5'
DARK = '#2E2E38'
INFO = '#7FD4F5'
DANGER = '#F06070'

pygame.display.set_caption('Chess')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font('freesansbold.ttf', 20)
big_font = pygame.font.Font('freesansbold.ttf', 50)


def draw_board():
	# draw border
	border = (PADDING, PADDING, BOARD_DIM, BOARD_DIM)
	pygame.draw.rect(screen, DARK, border, 3)

	# checkerboard pattern
	for row in range(8):
		for col in range(4):
			sq_x = PADDING + 2 * SQ_DIM * col
			sq_y = PADDING + SQ_DIM * row

			# apply x-offset to even rows
			if row % 2 == 0:
				sq_x += SQ_DIM

			pygame.draw.rect(screen, DARK, (sq_x, sq_y, SQ_DIM, SQ_DIM))


def draw_sidebar():
	# offset it to the right of the board
	sb_x = PADDING * 2 + BOARD_DIM
	sb_y = PADDING
	sb_w = SCREEN_WIDTH - sb_x - PADDING
	sb_h = SCREEN_HEIGHT - PADDING * 2
	pygame.draw.rect(screen, DARK, (sb_x, sb_y, sb_w, sb_h), 3)


def draw_pieces():
	for piece in b.board:
		if piece.is_empty():
			continue

		row, col = piece.index // 8, piece.index % 8
		p_x = PADDING + col * SQ_DIM
		p_y = PADDING + row * SQ_DIM
		screen.blit(piece_images[piece.symbol][0], (p_x, p_y))

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


b = Board()
valid_moves = b.get_valid_moves()

# load piece images
piece_images = {}
for piece in b.board:
	if piece.is_empty():
		continue

	path = f'../images/{piece.symbol}.png'
	img = pygame.image.load(path)
	img_normal = pygame.transform.smoothscale(img, (SQ_DIM, SQ_DIM))
	img_sm = pygame.transform.smoothscale(img, (SQ_DIM // 5, SQ_DIM // 5))

	piece_images[piece.symbol] = (img_normal, img_sm)

timer = pygame.time.Clock()
fps = 60
run = True
selected = None
selected_other_side = None
turn = 'w'
while run:
	timer.tick(fps)
	screen.fill(LIGHT)

	draw_board()
	# draw_sidebar()
	draw_pieces()

	if selected is not None:
		draw_moves(selected, valid_moves)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		if event.type == pygame.MOUSEBUTTONDOWN:
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
							valid_moves = b.get_valid_moves()
							turn = 'w' if turn == 'b' else 'b'
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

	pygame.display.flip()

pygame.quit()
