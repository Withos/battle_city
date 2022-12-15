import json
import os
from entities import *

def loadLevel(levelName):
    levelPath = LEVELS_PATH + "/" + levelName
    levelFile = open(levelPath)
    try:
        loadedLevel = json.load(levelFile)
    except ValueError:
        print(levelName + "is not a valid json file")
        levelFile.close()
        return None
    levelFile.close()
    return loadedLevel

def loadAllLevels():
    levels = []
    for file in os.listdir(LEVELS_PATH):
        if file.endswith(".json") and os.path.isfile(os.path.join(LEVELS_PATH, file)):
            level = loadLevel(file)
            if level != None:
                levels.append(level)
    return levels

def parseLoadedObjectToLevel(loadedObject):
    if isLoadedObjectValidLevel(loadedObject) == False:
        return None
    playerData = loadedObject.get(PLAYER_KEY)
    player = Player((playerData.get(LOCATION_X_KEY) * TILE) * SCALE, (playerData.get(LOCATION_Y_KEY) * TILE) * SCALE)

    level = Level(player)

    for tileData in loadedObject.get(TILES_KEY):
        posX = (tileData.get(LOCATION_X_KEY) * TILE) * SCALE + PLAYGROUNDLEFT
        posY = (tileData.get(LOCATION_Y_KEY) * TILE) * SCALE + PLAYGROUNDTOP
        tileType = tileData.get(TYPE_KEY)
        if tileType == BRICK_TILE_TYPE:
            level.addTile(posX, posY, BRICK)
        elif tileType == STEEL_TILE_TYPE:
            level.addTile(posX, posY, STEEL)
        elif tileType == CASTLE_TILE_TYPE:
            level.addTile(posX, posY, CASTLE)

    for enemyData in loadedObject.get(ENEMIES_KEY):
        posX = (enemyData.get(LOCATION_X_KEY) * TILE) * SCALE + PLAYGROUNDLEFT
        posY = (enemyData.get(LOCATION_Y_KEY) * TILE) * SCALE + PLAYGROUNDTOP
        enemyType = enemyData.get(TYPE_KEY)
        if enemyType == BASIC_ENEMY_TYPE:
            level.placeTank(posX, posY, BASICTANK)
        elif enemyType == POWER_ENEMY_TYPE:
            level.placeTank(posX, posY, POWERTANK)
        elif enemyType == SPEED_ENEMY_TYPE:
            level.placeTank(posX, posY, FASTTANK)
    return level
    

def isLoadedObjectValidLevel(loadedObject):
    if PLAYER_KEY not in loadedObject:
        return False
    if TILES_KEY not in loadedObject:
        return False
    if ENEMIES_KEY not in loadedObject:
        return False
    loadedPlayer = loadedObject.get(PLAYER_KEY)
    if LOCATION_X_KEY not in loadedPlayer or LOCATION_Y_KEY not in loadedPlayer:
        return False
    loadedTilesList = loadedObject.get(TILES_KEY)
    for loadedTile in loadedTilesList:
        if LOCATION_X_KEY not in loadedTile or LOCATION_Y_KEY not in loadedTile or TYPE_KEY not in loadedTile:
            return False
    loadedEnemiesList = loadedObject.get(ENEMIES_KEY)
    for loadedEnemy in loadedEnemiesList:
        if LOCATION_X_KEY not in loadedEnemy or LOCATION_Y_KEY not in loadedEnemy or TYPE_KEY not in loadedEnemy:
            return False
    return True

def parseAllLevels():
    loadedLevels = loadAllLevels()
    parsedLevels = []
    for loadedLevel in loadedLevels:
        parsedLevel = parseLoadedObjectToLevel(loadedLevel)
        if parsedLevel == None:
            print("Invalid level not loaded")
        else:
            parsedLevels.append(parsedLevel)
    return parsedLevels
