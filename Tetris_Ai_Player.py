import pygame
import random
import json
import numpy as np
import joblib

# Загружаем модель и энкодер
model = joblib.load('tetris_rf_model.pkl')

with open("action_encoder.json", "r") as f:
    action_encoder = json.load(f)

# Параметры игры
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
GRID_SIZE = 30
BOARD_WIDTH, BOARD_HEIGHT = 10, 20

# Стартовая игра
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris AI")
clock = pygame.time.Clock()

# Определяем формы фигур (матрицы 4x4 для каждой фигуры)
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'L': [[1, 0, 0],
          [1, 1, 1]],
    'J': [[0, 0, 1],
          [1, 1, 1]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]]
}

# Стартовая игра
class TetrisGame:
    def __init__(self):
        self.board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
        self.piece = self.random_piece()
        self.game_over = False

    def random_piece(self):
        shape = random.choice(list(SHAPES.keys()))
        return {'type': shape,
                'rotation': 0,
                'x': BOARD_WIDTH // 2 - 2,
                'y': 0}

    def rotate_piece(self):
        self.piece['rotation'] = (self.piece['rotation'] + 1) % 4

    def move_piece(self, dx, dy):
        self.piece['x'] += dx
        self.piece['y'] += dy

    def drop_piece(self):
        if self.piece['y'] < BOARD_HEIGHT - len(SHAPES[self.piece['type']]) and \
                np.all(self.board[self.piece['y'] + 1, self.piece['x']:self.piece['x'] + len(SHAPES[self.piece['type']][0])] == 0):
            self.piece['y'] += 1
        else:
            self.place_piece()
            self.piece = self.random_piece()  # Генерация новой фигуры
            if self.check_game_over():  # Проверка, если игра завершена
                self.game_over = True

    def place_piece(self):
        shape = SHAPES[self.piece['type']]
        for y in range(len(shape)):
            for x in range(len(shape[0])):
                if shape[y][x]:
                    self.board[self.piece['y'] + y, self.piece['x'] + x] = 1

    def check_game_over(self):
        # Проверка на верхнюю границу экрана
        shape = SHAPES[self.piece['type']]
        for y in range(len(shape)):
            for x in range(len(shape[0])):
                if shape[y][x] and self.board[self.piece['y'] + y, self.piece['x'] + x] != 0:
                    return True
        return False

    def get_state(self):
        return {
            'board': self.board.tolist(),
            'piece': self.piece
        }

    def apply_move(self, move):
        if move == "rotate":
            self.rotate_piece()
        elif move == "left":
            self.move_piece(-1, 0)
        elif move == "right":
            self.move_piece(1, 0)
        elif move == "down":
            self.drop_piece()

    def draw(self):
        screen.fill((0, 0, 0))  # Очистка экрана
        # Отображаем доску
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] == 1:
                    pygame.draw.rect(screen, (255, 255, 255), (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Отображаем текущую фигуру
        shape = SHAPES[self.piece['type']]
        for y in range(len(shape)):
            for x in range(len(shape[0])):
                if shape[y][x]:
                    pygame.draw.rect(screen, (0, 255, 0), ((self.piece['x'] + x) * GRID_SIZE, (self.piece['y'] + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        pygame.display.update()

# Инициализация игры
game = TetrisGame()

# Главный игровой цикл
while not game.game_over:
    state = game.get_state()
    board_flat = np.array(state['board']).flatten()
    piece_type_encoded = ord(state['piece']['type']) / 90
    input_vector = np.append(board_flat, piece_type_encoded)

    # Получаем действие от модели
    action = model.predict([input_vector])
    action = action_encoder[action[0]]

    # Применяем выбранное действие
    game.apply_move(action)

    # Отображаем экран
    game.draw()

    clock.tick(10)  # 10 кадров в секунду для замедления игры

print("Игра окончена!")