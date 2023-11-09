# Boo!
# Prototype 1

from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *


FPS = 30
SCREENWIDTH  = 560
SCREENHEIGHT = 504
BADGAPSIZE  = 80 
BASEY = SCREENHEIGHT * 0.79

# image and hitmask  dictionaries
IMAGES, HITMASKS = {}, {}

# list of players (tuple of 2 positions of ghost)
PLAYERS_LIST = (
    (
        'sprites/boo_up.png',
        'sprites/boo_down.png',
    )
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'sprites/level1back.png',
)

# list of obstacles
BAD_LIST = (
    'sprites/cross.png',
    'sprites/skeleton.png',
)


try:
    xrange
except NameError:
    xrange = range


def main():
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Boo!')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('sprites/0.png').convert_alpha(),
        pygame.image.load('sprites/1.png').convert_alpha(),
        pygame.image.load('sprites/2.png').convert_alpha(),
        pygame.image.load('sprites/3.png').convert_alpha(),
        pygame.image.load('sprites/4.png').convert_alpha(),
        pygame.image.load('sprites/5.png').convert_alpha(),
        pygame.image.load('sprites/6.png').convert_alpha(),
        pygame.image.load('sprites/7.png').convert_alpha(),
        pygame.image.load('sprites/8.png').convert_alpha(),
        pygame.image.load('sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('sprites/gameover.png').convert_alpha()
    # message sprite for start screen
    IMAGES['message'] = pygame.image.load('sprites/message.png').convert_alpha()
    # base sprite
    IMAGES['base'] = pygame.image.load('sprites/base.png').convert_alpha()

    while True:
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[0]).convert()

        IMAGES['player'] = (
            pygame.image.load('sprites/boo_up.png').convert_alpha(),
            pygame.image.load('sprites/boo_down.png').convert_alpha()
        )

        badindex = random.randint(0, len(BAD_LIST) - 1)
        IMAGES['bad'] = (
            pygame.transform.flip(
                pygame.image.load(BAD_LIST[badindex]).convert_alpha(), False, True),
            pygame.image.load(BAD_LIST[badindex]).convert_alpha(),
        )

        # hitmask for obstacles
        HITMASKS['bad'] = (
            getHitmask(IMAGES['bad'][0]),
            getHitmask(IMAGES['bad'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
        )

        movementInfo = showStartAnimation()
        crashInfo = gameplay(movementInfo)
        GameOverScreen(crashInfo)


def showStartAnimation():
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1])
    # iterator used to change playerIndex after every 5th iteration
    loop = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerFallVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # return values for gameplay
                return {
                    'playery': playery + playerFallVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # adjust playery, playerIndex, basex
        if (loop + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loop = (loop + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerFall(playerFallVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerFallVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def gameplay(movementInfo):
    score = playerIndex = loop = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 obstacles
    newbad1 = getRandomBad()
    newbad2 = getRandomBad()

    # list of upper obstacles
    upperbad = [
        {'x': SCREENWIDTH + 200, 'y': newbad1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newbad2[0]['y']},
    ]

    # list of lower obstacles
    lowerbad = [
        {'x': SCREENWIDTH + 200, 'y': newbad1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newbad2[1]['y']},
    ]

    badVelX = -4

    # player velocity, max velocity, downward accleration, accleration on jump
    playerVelY    =  -9   # player's velocity along Y, default same as playerJumped
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerMinVelY =  -8   # min vel along Y, max ascend speed
    playerAccY    =   1   # players downward accleration
    playerRot     =  45   # player's rotation
    playerVelRot  =   3   # angular speed
    playerRotThr  =  20   # rotation threshold
    playerJumpAcc =  -9   # players speed on jumping
    playerJumped = False  # True when player jumps


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerJumpAcc
                    playerJumped = True

        # check for crash here
        crashTest = Crash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperbad, lowerbad)
        if crashTest[0]:
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperbad': upperbad,
                'lowerbad': lowerbad,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for bad in upperbad:
            badMidPos = bad['x'] + IMAGES['bad'][0].get_width() / 2
            if badMidPos <= playerMidPos < badMidPos + 4:
                score += 1
                

        # playerIndex basex change
        if (loop + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loop = (loop + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerJumped:
            playerVelY += playerAccY
        if playerJumped:
            playerJumped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)

        # move obstacles to left
        for ubad, lbad in zip(upperbad, lowerbad):
            ubad['x'] += badVelX
            lbad['x'] += badVelX

        # add new obstacles when first obstacle is about to touch left of screen
        if 0 < upperbad[0]['x'] < 5:
            newbad = getRandomBad()
            upperbad.append(newbad[0])
            lowerbad.append(newbad[1])

        # remove first obstacle if its out of the screen
        if upperbad[0]['x'] < -IMAGES['bad'][0].get_width():
            upperbad.pop(0)
            lowerbad.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for ubad, lbad in zip(upperbad, lowerbad):
            SCREEN.blit(IMAGES['bad'][0], (ubad['x'], ubad['y']))
            SCREEN.blit(IMAGES['bad'][1], (lbad['x'], lbad['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        
        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def GameOverScreen(crashInfo):
    """crashes the player down and shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperbad, lowerbad = crashInfo['upperbad'], crashInfo['lowerbad']


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for ubad, lbad in zip(upperbad, lowerbad):
            SCREEN.blit(IMAGES['bad'][0], (ubad['x'], ubad['y']))
            SCREEN.blit(IMAGES['bad'][1], (lbad['x'], lbad['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))
        SCREEN.blit(IMAGES['gameover'], (180, 180))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerFall(playerFall):
    """oscillates the value of playerFall['val'] between 8 and -8"""
    if abs(playerFall['val']) == 8:
        playerFall['dir'] *= -1
    if playerFall['dir'] == 1:
         playerFall['val'] += 1
    else:
        playerFall['val'] -= 1


def getRandomBad():
    """returns a randomly generated obstacle"""
    # y of gap between upper and lower obstacles
    gapY = random.randrange(0, int(BASEY * 0.6 - BADGAPSIZE))
    gapY += int(BASEY * 0.2)
    badHeight = IMAGES['bad'][0].get_height()
    badX = SCREENWIDTH + 10

    return [
        {'x': badX, 'y': gapY - badHeight},  # upper 
        {'x': badX, 'y': gapY + BADGAPSIZE}, # lower 
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def Crash(player, upperbad, lowerbad):
    """returns True if player collders with base"""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        badW = IMAGES['bad'][0].get_width()
        badH = IMAGES['bad'][0].get_height()

        for ubad, lbad in zip(upperbad, lowerbad):
            # upper and lower rects
            ubadRect = pygame.Rect(ubad['x'], ubad['y'], badW, badH)
            lbadRect = pygame.Rect(lbad['x'], lbad['y'], badW, badH)

            # player and upper/lower obstacle hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['bad'][0]
            lHitmask = HITMASKS['bad'][1]

            # if ghost collided with ubad or lbad
            uCollide = pixelHit(playerRect, ubadRect, pHitMask, uHitmask)
            lCollide = pixelHit(playerRect, lbadRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelHit(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    main()
