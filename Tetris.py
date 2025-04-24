import pygame
import random
import json
import datetime

# Настройки
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20

# Цвета
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I
    (255, 255, 0),  # O
    (128, 0, 128),  # T
    (0, 255, 0),    # S
    (255, 0, 0),    # Z
    (0, 0, 255),    # J
    (255, 165, 0),  # L
]

SHAPES = [
    [[1, 1, 1, 1]],                          # I
    [[1, 1], [1, 1]],                        # O
    [[0, 1, 0], [1, 1, 1]],                  # T
    [[0, 1, 1], [1, 1, 0]],                  # S
    [[1, 1, 0], [0, 1, 1]],                  # Z
    [[1, 0, 0], [1, 1, 1]],                  # J
    [[0, 0, 1], [1, 1, 1]],                  # L
]

color_to_type = {
    (0, 255, 255): "I",
    (255, 255, 0): "O",
    (128, 0, 128): "T",
    (0, 255, 0): "S",
    (255, 0, 0): "Z",
    (0, 0, 255): "J",
    (255, 165, 0): "L"
}

class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def draw_grid(screen):
    for y in range(ROWS):
        for x in range(COLUMNS):
            rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_board(screen, board):
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, cell, rect)
    draw_grid(screen)

def create_board():
    return [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]

def valid_position(board, piece, offset_x=0, offset_y=0):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece.x + x + offset_x
                new_y = piece.y + y + offset_y
                if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                    return False
                if new_y >= 0 and board[new_y][new_x]:
                    return False
    return True

def lock_piece(board, piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                board[piece.y + y][piece.x + x] = piece.color

def clear_rows(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    lines_cleared = ROWS - len(new_board)
    for _ in range(lines_cleared):
        new_board.insert(0, [0 for _ in range(COLUMNS)])
    return new_board, lines_cleared

def get_piece_cells(piece):
    cells = []
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                cells.append([piece.x + x, piece.y + y])
    return cells

def get_unique_filename():
    now = datetime.datetime.now()
    return f"tetris_dataset_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Tetris Logger")
    clock = pygame.time.Clock()

    board = create_board()
    current_piece = Piece(random.choice(SHAPES), random.choice(COLORS))
    fall_time = 0
    fall_speed = 0.4
    last_move_time = 0
    move_delay = 150
    dataset = []
    score = 0

    running = True
    while running:
        screen.fill(BLACK)
        fall_time += clock.get_rawtime()
        last_move_time += clock.get_rawtime()
        clock.tick()

        keys = pygame.key.get_pressed()
        action = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if keys[pygame.K_LEFT] and last_move_time >= move_delay:
            if valid_position(board, current_piece, offset_x=-1):
                current_piece.x -= 1
                action = "left"
                last_move_time = 0
        elif keys[pygame.K_RIGHT] and last_move_time >= move_delay:
            if valid_position(board, current_piece, offset_x=1):
                current_piece.x += 1
                action = "right"
                last_move_time = 0
        elif keys[pygame.K_UP] and last_move_time >= move_delay:
            old_shape = current_piece.shape
            current_piece.rotate()
            if valid_position(board, current_piece):
                action = "rotate"
                last_move_time = 0
            else:
                current_piece.shape = old_shape
        elif keys[pygame.K_DOWN] and last_move_time >= move_delay:
            if valid_position(board, current_piece, offset_y=1):
                current_piece.y += 1
                action = "down"
                last_move_time = 0

        if fall_time / 1000 >= fall_speed:
            if valid_position(board, current_piece, offset_y=1):
                current_piece.y += 1
            else:
                lock_piece(board, current_piece)
                board, lines = clear_rows(board)
                score += lines * 100
                current_piece = Piece(random.choice(SHAPES), random.choice(COLORS))
                if not valid_position(board, current_piece):
                    running = False
            fall_time = 0

        if action:
            step = len(dataset) + 1
            piece_type = color_to_type.get(current_piece.color, "unknown")
            state = {
                "step": step,
                "board": [[1 if cell else 0 for cell in row] for row in board],
                "piece": {
                    "type": piece_type,
                    "color": current_piece.color,
                    "cells": get_piece_cells(current_piece)
                },
                "move": action
            }
            dataset.append(state)

        draw_board(screen, board)
        for cell in get_piece_cells(current_piece):
            rect = pygame.Rect(cell[0] * BLOCK_SIZE, cell[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, current_piece.color, rect)

        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.update()

    # Сохраняем с уникальным именем
    filename = get_unique_filename()
    with open(filename, "w") as f:
        json.dump(dataset, f, indent=2)

    pygame.quit()

if __name__ == "__main__":
    main()