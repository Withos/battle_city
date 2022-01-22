import pygame

pygame.init()

BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (107, 110, 114)

SCALE = 3

SCREENHEIGHT = 600
SCREENWIDTH = 800

WIDTHTILES = 13
HEIGHTTILES = 10
TILE = 16

PLAYGROUNDHEIGHT = HEIGHTTILES * TILE * SCALE
PLAYGROUNDWIDTH = WIDTHTILES * TILE * SCALE
PLAYGROUNDLEFT = int((SCREENWIDTH-PLAYGROUNDWIDTH)/3)
PLAYGROUNDTOP = int((SCREENHEIGHT-PLAYGROUNDHEIGHT)/2)

PIXELFONT1BIG = pygame.font.Font('fonts/BACKTO1982.ttf', 60)
PIXELFONT2BIG = pygame.font.Font('fonts/prstartk.ttf', 60)
PIXELFONT2SMALL = pygame.font.Font('fonts/prstartk.ttf', 20)

SPEED = 2

TILESCENTERS = []

for i in range(WIDTHTILES):
    for j in range(HEIGHTTILES):
        TILESCENTERS.append([(i * TILE) * SCALE + PLAYGROUNDLEFT, (j * TILE) * SCALE + PLAYGROUNDTOP])

BULLETSPEED = SPEED * 3
UP = 1
LEFT = 2
DOWN = 3
RIGHT = 4

BRICK = 1
STEEL = 2
BUSH = 3
WATER = 4
CASTLE = 5

BASICTANK = 1
FASTTANK = 2
POWERTANK = 3

NEUTRAL = 0
PLAYER = 1
ENEMIES = 2

SLOW = 0.5
NORMAL = 1
FAST = 1.5
