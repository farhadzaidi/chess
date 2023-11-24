import pygame
import re
from board import Board

pygame.init()

# the GUI and all of its assets are scaled with 
# the user's screen size
# SCREEN_WIDTH = pygame.display.Info().current_w // 1.15
# SCREEN_HEIGHT = pygame.display.Info().current_h // 1.15
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
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

# load piece images
pieces = {
    'p': 'bp', 'b': 'bb', 'n': 'bn',
    'r': 'br', 'q': 'bq', 'k': 'bk',
    'P': 'wp', 'B': 'wb', 'N': 'wn',
    'R': 'wr', 'Q': 'wq', 'K': 'wk',
}
for p, f in pieces.items():
	path = f'../images/{f}.png'
	img = pygame.image.load(path)
	img_normal = pygame.transform.smoothscale(img, (SQ_DIM, SQ_DIM))
	img_sm = pygame.transform.smoothscale(img, (SQ_DIM // 5, SQ_DIM // 5))

	# overwrite values with piece images
	pieces[p] = (img_normal, img_sm)

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
	for i, p in enumerate(b.board):
		if p == '+':
			continue

		row, col = i // 8, i % 8
		p_x = PADDING + col * SQ_DIM
		p_y = PADDING + row * SQ_DIM
		screen.blit(pieces[p][0], (p_x, p_y))

		if i == selected:
			outline = (p_x, p_y, SQ_DIM, SQ_DIM)
			pygame.draw.rect(screen, INFO, outline, 3)

def draw_moves(from_idx):
	for i in b.valid_moves.get(from_idx, []):
		row, col = i // 8, i % 8
		sq_x = PADDING + col * SQ_DIM
		sq_y = PADDING + row * SQ_DIM
		center = (sq_x + SQ_DIM // 2, sq_y + SQ_DIM // 2)
		radius = 7
		pygame.draw.circle(screen, INFO, center, radius)

b = Board()

timer = pygame.time.Clock()
fps = 60
run = True
selected = None
invalid = None
invalid_time = 0
while run:
	timer.tick(fps)
	screen.fill(LIGHT)

	draw_board()
	draw_sidebar()
	draw_pieces()

	if selected is not None:
		draw_moves(selected)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		if event.type == pygame.MOUSEBUTTONDOWN:
			col = (event.pos[0] - PADDING) // SQ_DIM
			row = (event.pos[1] - PADDING) // SQ_DIM

			if selected is None:
				# select piece
				from_idx = int(row * 8 + col)
				if b.board[from_idx] != '+':
					selected = from_idx
			else:
				# check if move is valid and make it
				to_idx = int(row * 8 + col)
				if to_idx in b.valid_moves.get(from_idx, []):
					b.make_move(from_idx, to_idx, b.board[from_idx])
				elif from_idx == to_idx:
					selected = None
				else:
					from_idx = to_idx
					selected = to_idx


	pygame.display.flip()

pygame.quit()