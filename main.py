import sys
from levelParser import parseAllLevels
from entities import *
pygame.init()

class StartGameScreen:
    def __init__(self):
        self._bctext = PIXELFONT1BIG.render('BATTLE CITY', True, (255, 255, 255))
        self._startgametext = PIXELFONT2SMALL.render('> PRESS SPACE <', True, (255, 255, 255))
        self._bcrect = self._bctext.get_rect(center = (SCREENWIDTH/2, SCREENHEIGHT/3))
        self._sgrect = self._startgametext.get_rect(center = (SCREENWIDTH/2, 2 * SCREENHEIGHT/3))

    def draw(self):
        screen.fill(BLACK)
        screen.blit(self._bctext, self._bcrect)
        screen.blit(self._startgametext, self._sgrect)


class YouWonScreen:
    def __init__(self, points):
        self._text = PIXELFONT2BIG.render('You Won!', True, (255, 255, 255))
        self._rect = self._text.get_rect(center=(SCREENWIDTH / 2, SCREENHEIGHT / 3))
        self._pointsText = PIXELFONT2SMALL.render('Your score: '+str(points), True, (255, 255, 255))
        self._rectPoints = self._pointsText.get_rect(center=(SCREENWIDTH / 2, 2 * SCREENHEIGHT / 3))

    def draw(self):
        screen.fill(BLACK)
        screen.blit(self._text, self._rect)
        screen.blit(self._pointsText, self._rectPoints)


class GameOverScreen:
    def __init__(self, points):
        self._text = PIXELFONT2BIG.render('GAME OVER', True, (161, 39, 14))
        self._rect = self._text.get_rect(center = (SCREENWIDTH/2, SCREENHEIGHT/3))
        self._pointsText = PIXELFONT2SMALL.render('Your score: '+str(points), True, (255, 255, 255))
        self._rectPoints = self._pointsText.get_rect(center=(SCREENWIDTH / 2, 2 * SCREENHEIGHT / 3))

    def draw(self):
        screen.fill(BLACK)
        screen.blit(self._text, self._rect)
        screen.blit(self._pointsText, self._rectPoints)

class Game:
    def __init__(self):
        self._FPS = 60
        self._Clock = pygame.time.Clock()
        self._levels = parseAllLevels()
        self._levelNumber = 0
        self._player = self._levels[self._levelNumber].getPlayer()
        self._currentLevel = self._levels[self._levelNumber]

    def drawBackground(self):
        screen.fill(GREY)
        pygame.draw.rect(screen, BLACK, pygame.Rect(PLAYGROUNDTOP, PLAYGROUNDLEFT, PLAYGROUNDWIDTH, PLAYGROUNDHEIGHT))

    def playerMove(self, keys):
        arrows = [keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT]]
        self._player.move(arrows)
        self._player.update(self._currentLevel.getTiles(), self._currentLevel.getTanks(), self._player)

    def startGame(self):
        if not self._levels:
            print("No levels loaded")
            pygame.quit()
            sys.exit()
        menuScreen = StartGameScreen()
        menu = True
        while menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        menu = False
                        self.loop()
            menuScreen.draw()
            pygame.display.update()
            self._Clock.tick(self._FPS)

    def gameWon(self, points):
        wonScreen = YouWonScreen(points)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pygame.quit()
                        sys.exit()
            wonScreen.draw()
            pygame.display.update()
            self._Clock.tick(self._FPS)

    def gameOver(self, points):
        overScreen = GameOverScreen(points)
        over = True
        while over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pygame.quit()
                        sys.exit()
            overScreen.draw()
            pygame.display.update()
            self._Clock.tick(self._FPS)

    def loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullet = self._player.fire()
                        if bullet is not None:
                            self._currentLevel.addBullet(bullet)
            keys = pygame.key.get_pressed()
            self.playerMove(keys)
            self.drawBackground()
            self._player.draw()
            if self._currentLevel.getCastle():
                if self._player.isDead() or self._currentLevel.getCastle().isDead():
                    points = 0
                    for level in self._levels:
                        points += level.getPoints()
                    self.gameOver(points)
            if len(self._currentLevel.getTanks()) < 1:
                self._levelNumber += 1
                if self._levelNumber >= len(self._levels):
                    points = 0
                    for level in self._levels:
                        points += level.getPoints()
                    self.gameWon(points)
                else:
                    self._currentLevel = self._levels[self._levelNumber]
            self._currentLevel.draw()
            pygame.display.update()
            self._Clock.tick(self._FPS)


if __name__ == '__main__':
    game = Game()
    game.startGame()
