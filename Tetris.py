import sys
import random
import pygame as pg
from math import sqrt
from typing import List, Tuple


# ! -----------------------------------------------------------------------------
# !                          G A M E   F U N C T I O N S
# ! -----------------------------------------------------------------------------

def main(dt) -> None:
    while True:
        event_handler()
        update_BG(dt)

        if Tetris.game_state == 'playing':
            update_game(dt)
        if Tetris.game_state == 'blinking':
            update_blinking(dt)

        draw(num_font)

        dt = FPSClock.tick(FPS)


def event_handler() -> None:
    game_state = Tetris.game_state

    for event in pg.event.get():
        # ! QUIT
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # ! INPUT
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE and game_state not in ['game_over', 'blinking']:
                if game_state == 'paused':
                    Tetris.game_state = 'playing'
                else:
                    Tetris.game_state = 'paused'

            elif event.key == pg.K_c:
                if Tetris.colour_scheme > 4: Tetris.colour_scheme = 0
                Tetris.colour_scheme += 1

            elif event.key == pg.K_x:
                if Tetris.colour_scheme < 1: Tetris.colour_scheme = 5
                Tetris.colour_scheme -= 1

            elif event.key == pg.K_h:
                Tetris.show_hint = False if Tetris.show_hint else True

            if game_state == 'paused':
                return

            elif event.key == pg.K_SPACE:
                if Tetris.game_state == 'playing':
                    Tetris.shape.delete()
                    while not Tetris.shape.unplaceable(): Tetris.shape.y += 1
                    Tetris.shape.y -= 1
                    Tetris.shape.falling_timer = 350
                elif game_state == 'game_over':
                    Tetris.reset()
                    Tetris.game_state = 'playing'
                else:
                    Tetris.game_state = 'playing'

            elif game_state == 'playing':
                if event.key == pg.K_UP:
                    Tetris.shape.rotate()

                elif event.key == pg.K_DOWN:
                    Tetris.falling_speed -= 330

                elif event.key == pg.K_LEFT:
                    Tetris.shape.move(-1)

                elif event.key == pg.K_RIGHT:
                    Tetris.shape.move(+1)

        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                Tetris.falling_speed = 350 - int(30*sqrt(Tetris.level)+19)

            elif event.key == pg.K_DOWN:
                Tetris.falling_speed = 350 - int(30*sqrt(Tetris.level)+19)



def update_game(dt) -> None:
    Tetris.shape.falling_timer += 1 * dt

    if Tetris.shape.falling_timer >= Tetris.falling_speed:
        Tetris.shape.drop()
        full_rows = Tetris.full_rows()
        if full_rows[0]:
            Tetris.blinking_index = full_rows[1]
            Tetris.game_state = 'blinking'

        if Tetris.rows_cleared >= Tetris.level*10 + 10:
            Tetris.level += 1

        Tetris.shape.falling_timer = 0

    # Finished game field
    Tetris.shape.delete()
    Tetris.shape.place()


def update_blinking(dt):
    Tetris.shape.falling_timer += 1 * dt
    t = Tetris.shape.falling_timer // 50
    if t % 2 == 0:
        for index in Tetris.blinking_index:
            Tetris.field[index] = [8]*10
    else:
        for index in Tetris.blinking_index:
            Tetris.field[index] = [0]*10

    if Tetris.shape.falling_timer >= 400:
        Tetris.shape.delete()
        Tetris.delete_rows(Tetris.blinking_index)
        Tetris.shape.place()
        Tetris.blinking_index = []
        Tetris.game_state = 'playing'


def update_BG(dt) -> None:
    if Background['BG_1']['y'] >= HEIGHT: Background['BG_1']['y'] = -HEIGHT
    elif Background['BG_2']['y'] >= HEIGHT: Background['BG_2']['y'] = -HEIGHT

    Background['BG_1']['y'] += 1*dt/50
    Background['BG_2']['y'] += 1*dt/50


# ! -----------------------------------------------------------------------------
# !                          D R A W   F U N C T I O N S
# ! -----------------------------------------------------------------------------

def draw(num_font) -> None:
    draw_BG()
    draw_border()
    draw_score(num_font)
    draw_game_field(Tetris.field)

    SCREEN.blit(mask_png, (420, 0))

    state = Tetris.game_state
    if state in ['playing', 'blinking']:
        draw_next_shape()
        if Tetris.show_hint and state == 'playing':
            draw_falling_hint()
    elif state == 'game_over':
        SCREEN.blit(game_over_png, (795, 165))
    elif state == 'paused':
        if Tetris.show_hint:
            draw_falling_hint()
        SCREEN.blit(controls_png, (850, 150))
        SCREEN.blit(paused_png, (480, 300))
    elif state == 'start':
        SCREEN.blit(start_png, (350, -50))

    pg.display.flip()


def draw_BG() -> None:
    SCREEN.blit(Background['BG_1']['img'], (0, Background['BG_1']['y']))
    SCREEN.blit(Background['BG_2']['img'], (0, Background['BG_2']['y']))


def draw_border() -> None:
    pg.draw.rect(SCREEN, (45, 45, 45), (420, 0, 420, 770))  # border
    pg.draw.rect(SCREEN, (10, 10, 10), (455, 35, 350, 700))  # black field


def draw_score(num_font) -> None:
    SCREEN.blit(level_png, (10, 15))
    _level_txt = num_font.render(str(Tetris.level), False, (230, 230, 230))
    SCREEN.blit(_level_txt, (30, 120))

    SCREEN.blit(score_png, (10, 260))
    _score_txt = num_font.render(str(Tetris.score).rjust(6, '0'), False, (230, 230, 230))
    SCREEN.blit(_score_txt, (30, 370))

    SCREEN.blit(high_score_png, (25, 500))
    _high_score_txt = num_font.render(str(Tetris.high_score).rjust(6, '0'), False, (230, 230, 230))
    SCREEN.blit(_high_score_txt, (30, 620))


def draw_game_field(field) -> None:
    for row in range(20):
        for column in range(10):
            if field[row][column] != 0:
                pg.draw.rect(SCREEN, get_colour(row, column), (35*column+35+420, 35*row+35, 32, 32))


def draw_next_shape() -> None:
    SCREEN.blit(next_png, (900, 30))

    for row in range(4):
        for column in range(4):
            if (column + row*4) in Tetris.next.shape[0]:
                _colour = colours[Tetris.next.colour_index] if Tetris.colour_scheme == 1 else get_colour(row, column)
                pg.draw.rect(SCREEN, _colour, (50*column+550+420, 50*row+180, 45, 45))

                SCREEN.blit(cube_png, (50*column+550+420, 50*row+180))


def draw_falling_hint() -> None:
    _Shape = Shape_Hint()
    for row in range(4):
        for column in range(4):
            if (column + row*4) in _Shape.shape:
                pg.draw.rect(SCREEN, _Shape.colour, ((column+Tetris.shape.x)*35+35+420, (row+_Shape.y)*35+35, 32, 32), 2)


def get_colour(row, column) -> Tuple[int, int, int]:
    _scheme = Tetris.colour_scheme
    _block = Tetris.field[row][column]
    if _scheme == 1 or row in Tetris.blinking_index:
            return colours[_block]  # current falling colour
    elif _scheme == 2:  # R
        return (255-5*row, 50-5*column, 11*row)
    elif _scheme == 3:  # G
        return (10*row, 245-11*row, 10*row)
    elif _scheme == 4:  # B
        return (45+3*row, 30, 255-8*row)
    return (250, 250, 250)  # W


# ! -----------------------------------------------------------------------------
# !                                   S E T U P
# ! -----------------------------------------------------------------------------

pg.init()

# GUI Setup
pg.font.init()
num_font = pg.font.Font('fonts\Final-Fantasy.ttf', 55)


# Clock setup
FPS = 20
FPSClock = pg.time.Clock()
dt = 1/FPS  # time since last frame.

# Window setup
WIDTH, HEIGHT = 1280, 770
CAPTION = 'Tetris 3.0'
ICON = pg.image.load('images\icon.png')
SCREEN = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(CAPTION)
pg.display.set_icon(ICON)

# Background setup
BG_img = pg.transform.scale(pg.image.load("images\stars_black.png"), (1280, 770)).convert_alpha()  # stars_2_BG.png
Background = {
    'BG_1': {'img': BG_img, 'y': 0},
    'BG_2': {'img': BG_img, 'y': HEIGHT}
    }

# Gameplay setup
start_png      = pg.transform.scale(pg.image.load("images\start.png"), (550, 550)).convert_alpha()
game_over_png  = pg.transform.scale(pg.image.load("images\game_over2.png"), (500, 500)).convert_alpha()
score_png      = pg.transform.scale(pg.image.load("images\score.png"), (250, 250)).convert_alpha()
level_png      = pg.transform.scale(pg.image.load("images\level.png"), (250, 250)).convert_alpha()
high_score_png = pg.transform.scale(pg.image.load("images\high_score.png"), (300, 300)).convert_alpha()
paused_png     = pg.transform.scale(pg.image.load("images\paused.png"), (300, 300)).convert_alpha()
controls_png   = pg.transform.scale(pg.image.load("images\controls.png"), (420, 450)).convert_alpha()
next_png       = pg.transform.scale(pg.image.load("images\\next.png"), (300, 300)).convert_alpha()
mask_png       = pg.image.load("images\mask.png").convert_alpha()
cube_mask_png  = pg.image.load("images\cube.png").convert_alpha()
cube_png = pg.transform.scale(pg.image.load("images\cube.png"), (50, 50)).convert_alpha()

with open("data\data.xml", "r") as f:
    high_score = int(f.read())

shapes = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
    [[4, 5, 9, 10], [2, 6, 5, 9]],  # Z
    [[6, 7, 9, 10], [1, 5, 6, 10]],  # S
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # J
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # L
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],  # T
    [[1, 2, 5, 6]],  # O
    ]

colours = [(10, 10, 10), (255, 0, 0), (0, 255, 0), (40, 40, 255), # Grey, Red, Green, Blue
            (0, 255, 255), (255, 255, 0), (255, 165, 0), (128, 0, 128),  # Cyan, Yellow, Orange, Purple
            (255, 255, 255)]  # White


# ! -----------------------------------------------------------------------------
# !                                 C L A S S E S
# ! -----------------------------------------------------------------------------

class Tetris():  # current game
    def __init__(self) -> None:
        self.field = [[0] * 10 for _ in range(20)]

        self.shape = Shape()
        self.next = NextShape()

        self.scoring = [100, 400, 900, 2000]
        self.score = 0
        self.high_score = high_score
        self.level = 0

        self.blinking_index = []  # indexes of blinking rows

        self.rows_cleared = 0
        self.falling_speed = 350
        self.colour_scheme = 1  # 1 - colour, 2 - gradient red, 3 - gradient green, 4 - gradient blu

        self.game_state: str = 'start'  # 'start', 'game_over', 'paused', 'playing', 'blinking'
        self.show_hint = True

    def full_rows(self) -> Tuple[bool, List[int]]:  # return if true + indexes of full rows
        _rows = []
        for row in range(20):
            if 0 not in self.field[row]:
                _rows.append(row)
        return (len(_rows) > 0, _rows)

    def delete_rows(self, rows: List[int]) -> None:  # delete full rows, add empty ones, add score
        for row in rows:
            self.field.pop(row)
            self.field.insert(0, [0]*10)

        self.rows_cleared += len(rows)
        self.score += self.scoring[len(rows)-1]

        if self.score > self.high_score:
            with open('data\data.xml', 'w') as f:
                f.write(str(self.score))
                self.high_score = self.score

    def reset(self) -> None:
        self.field = [[0] * 10 for _ in range(20)]
        self.score = 0
        self.rows_cleared = 0
        self.level = 0
        self.falling_speed = 350

        self.shape.colour_index = random.randint(1, 7)
        self.shape.shape = random.choice(shapes)
        self.next.colour_index = random.randint(1, 7)
        self.next.shape = random.choice(shapes)


class Shape():
    def __init__(self, colour=random.randint(1, 7), shape=random.choice(shapes)) -> None:
        self.falling_timer = 0
        self.colour_index = colour
        self.shape = shape
        self.rotation = 0
        self.x = 3
        self.y = 0

    def move(self, side: int) -> None:
        self.delete()
        self.x += side
        if self.unplaceable():
            self.x -= side

    def rotate(self) -> None:
        self.delete()
        _cache = self.rotation

        _rotations = len(self.shape)  # possible rotations
        self.rotation = 0 if self.rotation == _rotations-1 else self.rotation + 1

        if self.unplaceable() and self.x > 10:
            self.move(-1)
        if self.unplaceable():
            self.rotation = _cache

    def place(self) -> None:  # place the shape into field
        for row in range(4):
            for column in range(4):
                if (column + row*4) in self.shape[self.rotation]:
                    Tetris.field[row + self.y][column + self.x] = self.colour_index  #99

    def set(self) -> None:  # freeze the shape in place
        for row in range(4):
            for column in range(4):
                if (column + row*4) in self.shape[self.rotation]:
                    Tetris.field[row + self.y][column + self.x] = self.colour_index
        Tetris.shape = Shape(Tetris.next.colour_index, Tetris.next.shape)
        _pack = Tetris.next.pack
        Tetris.next = NextShape(_pack)

    def drop(self) -> None:
        self.delete()
        self.y += 1
        if self.unplaceable():
            self.y -= 1
            self.set()
            if self.y == 0:
                Tetris.game_state = 'game_over'

    def delete(self) -> None:  # delete shape from its current location
        for row in range(4):
            for column in range(4):
                if (column + row*4) in self.shape[self.rotation]:
                    Tetris.field[row + self.y][column + self.x] = 0

    def unplaceable(self) -> bool:
        for row in range(4):
            for column in range(4):
                if (column + row*4) in self.shape[self.rotation]:
                    if (row + self.y) > 19 or (column + self.x) > 9 or \
                        (column + self.x) < 0 or \
                            (Tetris.field[row + self.y][column + self.x] != 0):
                        return True


class Shape_Hint():
    def __init__(self) -> None:
        self.shape = Tetris.shape.shape[Tetris.shape.rotation]
        self.y = self.get_y(Tetris.shape.y)
        self.colour = colours[Tetris.shape.colour_index] if Tetris.colour_scheme == 1 else get_colour(self.y, 3)

    def get_y(self, _y) -> int:  # return y of the outline
        Tetris.shape.delete()
        while not self.unplaceable(_y): _y += 1
        Tetris.shape.place()
        return _y-1

    def unplaceable(self, _y) -> bool:
        for row in range(4):
            for column in range(4):  # cant be placed inside shapes or borders
                if ((column + row*4) in self.shape) and ((row + _y) > 19 or
                     Tetris.field[row + _y][column + Tetris.shape.x]):
                        return True


class NextShape():
    def __init__(self, pack=[0, 1, 2, 3, 4, 5, 6]) -> None:
        self.pack = pack
        self.shape = self.shape_from_pack()
        self.colour_index = random.randint(1, 7)

    def shape_from_pack(self) -> List[List[int]]:
        if self.pack == []:
            self.pack = [0, 1, 2, 3, 4, 5, 6]

        _shape_index = random.choice(self.pack)
        self.pack.remove(_shape_index)

        return shapes[_shape_index]


# ! START
Tetris = Tetris()
main(dt)
