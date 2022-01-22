import random
import sys
from const import *
import pygame
from pygame import mixer

pygame.init()


def rot_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect


class Tank:
    def __init__(self, hp, xPos, yPos, spritePath):
        self._hp = hp
        self.tmp = pygame.image.load(spritePath)
        self.surf = pygame.Surface((self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))
        self.rect = self.surf.get_rect(center=(xPos, yPos))
        self.image = pygame.transform.scale(self.tmp, (self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))
        self.originalImage = pygame.transform.scale(self.tmp, (self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))
        self.speed = SPEED
        self.xChange = 0
        self.yChange = 0
        self.direction = UP
        self.fired = 0
        self.shots = 0
        self.bulletSpeed = NORMAL
        self.team = NEUTRAL
        self._points = 0

    def setHP(self, hp):
        self._hp = hp

    def setSprite(self, sprite):
        self.image = sprite

    def getHP(self):
        return self._hp

    def getSprite(self):
        return self.image

    def getTeam(self):
        return self.team

    def getBulletSpeed(self):
        return self.bulletSpeed

    def getPoints(self):
        return self._points

    def draw(self):
        screen.blit(self.image, self.rect)

    def changeSpeed(self, x, y):
        self.xChange = x
        self.yChange = y

    def isDead(self):
        return self._hp < 1

    def fire(self):
        if self.fired >= self.shots:
            return None
        bullet = None
        if self.direction == UP:
            bullet = Bullet(self.rect.centerx, self.rect.top, UP, self)
        elif self.direction == RIGHT:
            bullet = Bullet(self.rect.right, self.rect.centery, RIGHT, self)
        elif self.direction == DOWN:
            bullet = Bullet(self.rect.centerx, self.rect.bottom, DOWN, self)
        elif self.direction == LEFT:
            bullet = Bullet(self.rect.left, self.rect.centery, LEFT, self)
        bullet.fire()
        self.fired += 1
        return bullet

    def changeDirection(self, direction):
        angle = (direction - 1) * 90
        self.image, self.rect = rot_center(self.originalImage, self.rect, angle)
        self.direction = direction

    def bulletHit(self):
        self.fired -= 1

    def hit(self, bullet):
        if self.team == bullet.getParentTank().getTeam():
            return
        self._hp -= 1

    def moveTo(self, xPos, yPos):
        self.rect.update(xPos, yPos, self.rect.width, self.rect.height)

    def update(self, tiles, tanks, player):
        self.rect.x += self.xChange
        self.rect.y += self.yChange
        for tile in tiles:
            for quadrant in tile.getQuadrants():
                if self.rect.colliderect(quadrant.rect):
                    if self.direction == UP:
                        self.rect.top = quadrant.rect.bottom
                    elif self.direction == LEFT:
                        self.rect.left = quadrant.rect.right
                    elif self.direction == DOWN:
                        self.rect.bottom = quadrant.rect.top
                    elif self.direction == RIGHT:
                        self.rect.right = quadrant.rect.left

        for tank in tanks:
            if tank != self:
                if self.rect.colliderect(tank.rect):
                    if self.direction == UP:
                        self.rect.x -= self.xChange
                        self.rect.y -= self.yChange
                    elif self.direction == LEFT:
                        self.rect.x -= self.xChange
                        self.rect.y -= self.yChange
                    elif self.direction == DOWN:
                        self.rect.x -= self.xChange
                        self.rect.y -= self.yChange
                    elif self.direction == RIGHT:
                        self.rect.x -= self.xChange
                        self.rect.y -= self.yChange

        if self != player:
            if self.rect.colliderect(player.rect):
                if self.direction == UP:
                    self.rect.x -= self.xChange
                    self.rect.y -= self.yChange
                elif self.direction == LEFT:
                    self.rect.x -= self.xChange
                    self.rect.y -= self.yChange
                elif self.direction == DOWN:
                    self.rect.x -= self.xChange
                    self.rect.y -= self.yChange
                elif self.direction == RIGHT:
                    self.rect.x -= self.xChange
                    self.rect.y -= self.yChange


class Player(Tank):
    def __init__(self, xPos, yPos):
        super().__init__(1, xPos, yPos, 'sprites/player_tank.png')
        self.team = PLAYER
        self.shots = 1
        self.bulletSpeed = SLOW
        self.lifes = 3

    def move(self, arrows):
        if self.rect.top > self.speed + PLAYGROUNDTOP:
            if arrows[0]:
                self.changeSpeed(0, -self.speed)
                self.changeDirection(UP)
                return
        if self.rect.bottom < PLAYGROUNDTOP + PLAYGROUNDHEIGHT - self.speed:
            if arrows[1]:
                self.changeSpeed(0, self.speed)
                self.changeDirection(DOWN)
                return
        if self.rect.left - PLAYGROUNDLEFT > self.speed:
            if arrows[2]:
                self.changeSpeed(-self.speed, 0)
                self.changeDirection(LEFT)
                return
        if self.rect.right < PLAYGROUNDLEFT + PLAYGROUNDWIDTH - self.speed:
            if arrows[3]:
                self.changeSpeed(self.speed, 0)
                self.changeDirection(RIGHT)
                return

    def isDead(self):
        return self.lifes < 1

    def hit(self, bullet):
        if self.team == bullet.getParentTank().getTeam():
            return
        self._hp -= 1
        if self._hp < 1:
            self.lifes -= 1
            self._hp = 1
            self.rect.x = 500
            self.rect.y = 400

    def update(self, tiles, tanks, player):
        super().update(tiles, tanks, player)
        self.xChange = 0
        self.yChange = 0


class Enemy(Tank):
    def __init__(self, hp, xPos, yPos, spritePath):
        super().__init__(hp, xPos, yPos, spritePath)
        self.team = ENEMIES
        self.toDirectionChange = 60
        self.shots = 1
        self.fireTimer = random.randint(20, 60)

    def changeSpeedtoDirection(self):
        if self.direction == UP:
            super().changeSpeed(0, -self.speed)
        elif self.direction == DOWN:
            super().changeSpeed(0, self.speed)
        elif self.direction == LEFT:
            super().changeSpeed(-self.speed, 0)
        elif self.direction == RIGHT:
            super().changeSpeed(self.speed, 0)

    def update(self, tiles, tanks, player):
        super().update(tiles, tanks, player)
        if self.rect.top < PLAYGROUNDTOP:
            self.rect.top = PLAYGROUNDTOP
        if self.rect.bottom > PLAYGROUNDTOP + PLAYGROUNDHEIGHT:
            self.rect.bottom = PLAYGROUNDTOP + PLAYGROUNDHEIGHT
        if self.rect.left < PLAYGROUNDLEFT:
            self.rect.left = PLAYGROUNDLEFT
        if self.rect.right > PLAYGROUNDLEFT + PLAYGROUNDWIDTH:
            self.rect.right = PLAYGROUNDLEFT + PLAYGROUNDWIDTH

    def fire(self):
        if self.fireTimer < 1:
            self.fireTimer = random.randint(60, 180)
            return super().fire()
        else:
            self.fireTimer -= 1

    def move(self):
        self.toDirectionChange -= 1
        if self.toDirectionChange < 1:
            self.changeDirection(random.choice([UP, LEFT, DOWN, RIGHT]))
            self.toDirectionChange = random.randint(60, 180)
            self.changeSpeedtoDirection()


class BasicEnemy(Enemy):
    def __init__(self, xPos, yPos):
        super().__init__(1, xPos, yPos, 'sprites/basic_tank.png')
        self.speed = SLOW * SPEED
        self.bulletSpeed = SLOW
        self._points = 100


class FastEnemy(Enemy):
    def __init__(self, xPos, yPos):
        super().__init__(1, xPos, yPos, 'sprites/fast_tank.png')
        self.speed = FAST * SPEED
        self.bulletSpeed = NORMAL
        self._points = 200


class PowerEnemy(Enemy):
    def __init__(self, xPos, yPos):
        super().__init__(1, xPos, yPos, 'sprites/power_tank.png')
        self.speed = NORMAL * SPEED
        self.bulletSpeed = FAST
        self._points = 300


class Quadrant:
    def __init__(self):
        self.image = None
        self.rect = None
        self.surf = None
        self._parentTile = None

    def hit(self, bullet):
        self._parentTile.quadrantHit(self)

    def draw(self):
        screen.blit(self.image, self.rect)


class BrickQuadrant(Quadrant):
    def __init__(self, parentTile, topleftx, toplefty):
        super().__init__()
        self._parentTile = parentTile
        self.tmp = pygame.image.load('sprites/brick.png')
        self.surf = pygame.Surface((self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))
        self.rect = self.surf.get_rect(topleft=(topleftx, toplefty))
        self.image = pygame.transform.scale(self.tmp, (self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))


class SteelQuadrant(Quadrant):
    def __init__(self, parentTile, topleftx, toplefty):
        super().__init__()
        self._parentTile = parentTile
        self.tmp = pygame.image.load('sprites/steel.png')
        self.surf = pygame.Surface((self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))
        self.rect = self.surf.get_rect(topleft=(topleftx, toplefty))
        self.image = pygame.transform.scale(self.tmp, (self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))


class CastleQuadrant(Quadrant):
    def __init__(self, parentTile, topleftx, toplefty, spriteNumber):
        super().__init__()
        self._parentTile = parentTile
        self.tmp = pygame.image.load('sprites/castle_'+str(spriteNumber)+'.png')
        self.surf = pygame.Surface((self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))
        self.rect = self.surf.get_rect(topleft=(topleftx, toplefty))
        self.image = pygame.transform.scale(self.tmp, (self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))


class Tile:
    def __init__(self):
        self._quadrants = []

    def draw(self):
        for quadrant in self._quadrants:
            quadrant.draw()

    def getQuadrants(self):
        return self._quadrants

    def quadrantHit(self, quadrant):
        pass


class BrickTile(Tile):
    def __init__(self, topLeftX, topLeftY):
        super().__init__()
        self._quadrants.append(BrickQuadrant(self, topLeftX, topLeftY))
        self._quadrants.append(BrickQuadrant(self, topLeftX+8*SCALE, topLeftY))
        self._quadrants.append(BrickQuadrant(self, topLeftX, topLeftY+8*SCALE))
        self._quadrants.append(BrickQuadrant(self, topLeftX+8*SCALE, topLeftY + 8 * SCALE))

    def quadrantHit(self, quadrant):
        self.getQuadrants().remove(quadrant)


class Castle(Tile):
    def __init__(self, topLeftX, topLeftY):
        super().__init__()
        self._quadrants.append(CastleQuadrant(self, topLeftX, topLeftY, 1))
        self._quadrants.append(CastleQuadrant(self, topLeftX + 8 * SCALE, topLeftY, 2))
        self._quadrants.append(CastleQuadrant(self, topLeftX, topLeftY + 8 * SCALE, 3))
        self._quadrants.append(CastleQuadrant(self, topLeftX + 8 * SCALE, topLeftY + 8 * SCALE, 4))
        self.destroyed = False

    def quadrantHit(self, quadrant):
        self.destroyed = True

    def isDead(self):
        return self.destroyed


class SteelTile(Tile):
    def __init__(self, topLeftX, topLeftY):
        super().__init__()
        self._quadrants.append(SteelQuadrant(self, topLeftX, topLeftY))
        self._quadrants.append(SteelQuadrant(self, topLeftX+8*SCALE, topLeftY))
        self._quadrants.append(SteelQuadrant(self, topLeftX, topLeftY+8*SCALE))
        self._quadrants.append(SteelQuadrant(self, topLeftX+8*SCALE, topLeftY + 8 * SCALE))


class Bullet:
    def __init__(self, xPos, yPos, direction, parentTank):
        self.xPos = xPos
        self.yPos = yPos
        self.direction = direction
        self.parentTank = parentTank
        self.xChange = 0
        self.yChange = 0
        self.tmp = pygame.image.load('sprites/bullet.png')
        self.surf = pygame.Surface((self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))
        self.rect = self.surf.get_rect(center=(xPos, yPos))
        self.image = pygame.transform.scale(self.tmp, (self.tmp.get_width() * SCALE, self.tmp.get_height() * SCALE))

    def fire(self):
        if self.direction == UP:
            self.yChange = -BULLETSPEED * self.parentTank.getBulletSpeed()
        elif self.direction == RIGHT:
            self.xChange = BULLETSPEED * self.parentTank.getBulletSpeed()
            self.image, self.rect = rot_center(self.image, self.rect, 270)
        elif self.direction == DOWN:
            self.yChange = BULLETSPEED * self.parentTank.getBulletSpeed()
            self.image, self.rect = rot_center(self.image, self.rect, 180)
        elif self.direction == LEFT:
            self.xChange = -BULLETSPEED * self.parentTank.getBulletSpeed()
            self.image, self.rect = rot_center(self.image, self.rect, 90)

    def getParentTank(self):
        return self.parentTank

    def update(self, tiles, tanks, player, bullets):
        self.rect.x += self.xChange
        self.rect.y += self.yChange

        for bullet in bullets:
            if self != bullet:
                if self.rect.colliderect(bullet.rect):
                    self.parentTank.bulletHit()
                    return self

        if PLAYGROUNDLEFT > self.rect.left or \
                self.rect.right > PLAYGROUNDLEFT+PLAYGROUNDWIDTH or \
                PLAYGROUNDTOP > self.rect.top or \
                self.rect.bottom > PLAYGROUNDTOP+PLAYGROUNDHEIGHT:
            self.parentTank.bulletHit()
            return self

        hitObjects = []
        for tile in tiles:
            for quadrant in tile.getQuadrants():
                if self.rect.colliderect(quadrant.rect):
                    hitObjects.append(quadrant)

        for tank in tanks:
            if tank != self.parentTank:
                if self.rect.colliderect(tank.rect):
                    hitObjects.append(tank)

        if self.parentTank != player:
            if self.rect.colliderect(player.rect):
                hitObjects.append(player)

        for obj in hitObjects:
            obj.hit(self)

        if hitObjects:
            self.parentTank.bulletHit()
            return self
        else:
            return None

    def draw(self):
        screen.blit(self.image, self.rect)


class Animation:
    def __init__(self, sprites, xPos, yPos):
        self._sprites = []
        self._rects = []
        self._surfs = []
        self._animationTime = 60
        self._timeLeft = self._animationTime
        self._currentSprite = 0
        self._spriteDuration = 0

        for spritePath in sprites:
            self._sprites.append(pygame.image.load(spritePath))
            self._surfs.append(pygame.Surface(((self._sprites[-1].get_width()) * SCALE, self._sprites[-1].get_height())))
            self._rects.append(self._surfs[-1].get_rect(center=(xPos, yPos)))
            self._sprites[-1] = pygame.transform.scale(self._sprites[-1],
                                    (self._sprites[-1].get_width() * SCALE, self._sprites[-1].get_height() * SCALE))

    def update(self):
        self._timeLeft -= 1
        if self._timeLeft < 1:
            return self
        self._spriteDuration -= 1
        if self._spriteDuration < 1:
            self._currentSprite += 1
            self._spriteDuration = self._animationTime / len(self._sprites)

    def draw(self):
        screen.blit(self._sprites[self._currentSprite], self._rects[self._currentSprite])


class Explosion(Animation):
    def __init__(self, xPos, yPos):
        super().__init__(['sprites/explosion_1.png', 'sprites/explosion_2.png', 'sprites/explosion_1.png'], xPos, yPos - 15)
        self._animationTime = 21
        self._timeLeft = self._animationTime
        self._currentSprite = 0
        self._spriteDuration = self._animationTime/len(self._sprites)


class Level:
    def __init__(self, player):
        self._tiles = []
        self._tanks = []
        self._bullets = []
        self._player = player
        self._animations = []
        self._numberOfEnemies = 0
        self._castle = None
        self._spawnTimer = 0
        self._points = 0

    def addTile(self, topLeftX, topLeftY, type):
        if type == BRICK:
            self._tiles.append(BrickTile(topLeftX, topLeftY))
        if type == CASTLE:
            self._castle = Castle(topLeftX, topLeftY)
            self._tiles.append(self._castle)
        if type == STEEL:
            self._tiles.append(SteelTile(topLeftX, topLeftY))

    def getTiles(self):
        return self._tiles

    def getCastle(self):
        return self._castle

    def getBullets(self):
        return self._bullets

    def getPoints(self):
        return self._points

    def addBullet(self, bullet):
        self._bullets.append(bullet)

    def removeBullet(self, bullet):
        self._bullets.remove(bullet)

    def addTank(self, tank):
        self._tanks.append(tank)

    def removeTank(self, tank):
        self._tanks.remove(tank)

    def removeAnimation(self, animation):
        self._animations.remove(animation)

    def getTanks(self):
        return self._tanks

    def spawnTank(self, tankType):
        if tankType == BASICTANK:
            tank = BasicEnemy(0, 0)
        elif tankType == FASTTANK:
            tank = FastEnemy(0, 0)
        elif tankType == POWERTANK:
            tank = PowerEnemy(0, 0)
        else:
            print("theres no such tank")
            return
        sequance = random.sample(TILESCENTERS, len(TILESCENTERS))
        for center in sequance:
            collision = False
            tank.rect.x, tank.rect.y = center
            for tile in self._tiles:
                for quadrant in tile.getQuadrants():
                    if tank.rect.colliderect(quadrant.rect):
                        collision = True
                        break
                else:
                    continue
                break
            for tank1 in self._tanks:
                if tank1 != tank:
                    if tank.rect.colliderect(tank1.rect):
                        collision = True
                        break
            if not collision:
                self.addTank(tank)
                return True
        return False

    def spawnRandomTank(self):
        types = [BASICTANK, FASTTANK, POWERTANK]
        weights = [0.6, 0.3, 0.1]
        tanktype = random.choices(types, weights)
        if self.spawnTank(tanktype[0]):
            self._numberOfEnemies -= 1

    def updateTanks(self):
        if self._spawnTimer > 0:
            self._spawnTimer -= 1
        if len(self._tanks) < 3 and self._numberOfEnemies > 0:
            if self._spawnTimer < 1:
                self.spawnRandomTank()
                self._numberOfEnemies -= 1
                self._spawnTimer = 15
        firedBullets = []
        for tank in self._tanks:
            tank.move()
            tank.update(self._tiles, self._tanks, self._player)
            firedBullets.append(tank.fire())

        return firedBullets

    def updateBullets(self):
        delBullets = []
        for bullet in self._bullets:
            delBullets.append(bullet.update(self._tiles, self._tanks, self._player, self._bullets))

        for bullet in delBullets:
            if bullet is not None:
                self._animations.append(Explosion(bullet.rect.centerx, bullet.rect.centery))
                self.removeBullet(bullet)

    def updateAnimations(self):
        delAnimations = []

        for animation in self._animations:
            tmp = animation.update()
            if isinstance(tmp, Animation):
                delAnimations.append(tmp)

        for animation in delAnimations:
            self.removeAnimation(animation)

    def draw(self):
        for tile in self._tiles:
            tile.draw()
        for tank in self._tanks:
            if tank.isDead():
                self._animations.append(Explosion(tank.rect.centerx, tank.rect.centery))
                self._points += tank.getPoints()
                self._tanks.remove(tank)
                continue
            tank.draw()
        for bullet in self._bullets:
            bullet.draw()
        for animation in self._animations:
            animation.draw()

        self.updateAnimations()
        self.updateBullets()
        firedBullets = self.updateTanks()
        for bullet in firedBullets:
            if isinstance(bullet, Bullet):
                self._bullets.append(bullet)

    def buildCastle(self):
        self.addTile(PLAYGROUNDLEFT + PLAYGROUNDWIDTH / 2 - TILE * SCALE / 2,
                     PLAYGROUNDTOP + PLAYGROUNDHEIGHT - TILE * SCALE, CASTLE)
        self.addTile(PLAYGROUNDLEFT + PLAYGROUNDWIDTH / 2 - TILE * SCALE / 2 - TILE * SCALE,
                     PLAYGROUNDTOP + PLAYGROUNDHEIGHT - TILE * SCALE, BRICK)
        self.addTile(PLAYGROUNDLEFT + PLAYGROUNDWIDTH / 2 - TILE * SCALE / 2 - TILE * SCALE,
                     PLAYGROUNDTOP + PLAYGROUNDHEIGHT - 2 * TILE * SCALE, BRICK)
        self.addTile(PLAYGROUNDLEFT + PLAYGROUNDWIDTH / 2 - TILE * SCALE / 2,
                     PLAYGROUNDTOP + PLAYGROUNDHEIGHT - 2 * TILE * SCALE, BRICK)
        self.addTile(PLAYGROUNDLEFT + PLAYGROUNDWIDTH / 2 - TILE * SCALE / 2 + TILE * SCALE,
                     PLAYGROUNDTOP + PLAYGROUNDHEIGHT - 2 * TILE * SCALE, BRICK)
        self.addTile(PLAYGROUNDLEFT + PLAYGROUNDWIDTH / 2 - TILE * SCALE / 2 + TILE * SCALE,
                     PLAYGROUNDTOP + PLAYGROUNDHEIGHT - TILE * SCALE, BRICK)


class TestLevel(Level):
    def __init__(self, player):
        super().__init__(player)
        self._numberOfEnemies = 0

    def build(self):
        for center in TILESCENTERS:
            self.addTile(*center, BRICK)


class Level2(Level):
    def __init__(self, player):
        super().__init__(player)
        self._numberOfEnemies = 10

    def build(self):
        self.buildCastle()

        self.addTank(BasicEnemy(400,100))
        self.addTank(BasicEnemy(200,100))
        self.addTank(FastEnemy(600, 300))



class Level1(Level):
    def __init__(self, player):
        super().__init__(player)
        self._numberOfEnemies = 10

    def build(self):
        self.buildCastle()

        self._tanks.append(BasicEnemy(*TILESCENTERS[11]))
        self._tanks.append(BasicEnemy(*TILESCENTERS[16]))
        self._tanks.append(BasicEnemy(*TILESCENTERS[56]))
        for i in range(1, WIDTHTILES, 2):
            for j in range(1, 4):
                self.addTile(PLAYGROUNDLEFT + i * TILE * SCALE, PLAYGROUNDTOP + j * TILE * SCALE, BRICK)


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
        self._player = Player(500, 400)
        self._levels = []
        self._levels.append(Level1(self._player))
        self._levels.append(Level2(self._player))
        self._levelNumber = 0
        self._currentLevel = self._levels[self._levelNumber]


    def drawBackground(self):
        screen.fill(GREY)
        pygame.draw.rect(screen, BLACK, pygame.Rect(PLAYGROUNDTOP, PLAYGROUNDLEFT, PLAYGROUNDWIDTH, PLAYGROUNDHEIGHT))

    def playerMove(self, keys):
        arrows = [keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT]]
        self._player.move(arrows)
        self._player.update(self._currentLevel.getTiles(), self._currentLevel.getTanks(), self._player)

    def startGame(self):
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
                        self._currentLevel.build()
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
                    self._currentLevel.build()
            self._currentLevel.draw()
            pygame.display.update()
            self._Clock.tick(self._FPS)


if __name__ == '__main__':
    screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.flip()
    game = Game()
    game.startGame()
