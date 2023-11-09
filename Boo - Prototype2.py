# Boo!
# Final Prototype

# Initial set up

# Importing modules
from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *

# Variables for core values used within the game
FPS = 30
SCREENWIDTH  = 560
SCREENHEIGHT = 504
BADGAPSIZE = 80
BASEY = SCREENHEIGHT * 0.79

# image, sounds and hitmask  dictionaries
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

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
    'sprites/cross1.png',
    'sprites/skeleton.png',
)

# Validation for whether code run in either Python 2 or 3
try:
    xrange
except NameError:
    xrange = range

def main(): # sets up game values and calls all other functions
    
    global SCREEN, FPSCLOCK
    pygame.init() # initialises all imported Pygame modules
    
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    
    pygame.display.set_caption('Boo!')                 # sets caption in window header to name of the game
    gameIcon = pygame.image.load('sprites/boo_up.png') # sets icon in  window header to ghost sprite
    pygame.display.set_icon(gameIcon)

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
    IMAGES['gameover'] = pygame.image.load('sprites/gameover1.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('sprites/message1.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('sprites/base.png').convert_alpha()
    # new high score
    IMAGES['newhighscore'] = pygame.image.load('sprites/newhighscore.png').convert_alpha()
    # minus 
    IMAGES['minus'] = pygame.image.load('sprites/minus1.png').convert_alpha()
    # plus
    IMAGES['plus'] = pygame.image.load('sprites/plus5.png').convert_alpha()
    # your score
    IMAGES['yourscore'] = pygame.image.load('sprites/yourscore.png').convert_alpha()
    # high score
    IMAGES['highscore'] = pygame.image.load('sprites/highscore.png').convert_alpha()
    # points to high score
    IMAGES['pointsto'] = pygame.image.load('sprites/pointsto.png').convert_alpha()

    # POWER-UPS
    # Power-up icons
    IMAGES['powerups'] = (
        pygame.image.load('sprites/plus5.png').convert_alpha(),
        pygame.image.load('sprites/gap.png').convert_alpha(),
        pygame.image.load('sprites/minus1.png').convert_alpha(),
        pygame.image.load('sprites/speed.png').convert_alpha(),
        )
    # Power-up messages
    IMAGES['powerupsmessages'] = (
        pygame.image.load('sprites/plus5message.png').convert_alpha(),
        pygame.image.load('sprites/gapmessage.png').convert_alpha(),
        pygame.image.load('sprites/minus1message.png').convert_alpha(),
        pygame.image.load('sprites/speedmessage.png').convert_alpha(),
        )

    # SOUND
    # Determines best sound file type for platform
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    # Sets 'SOUNDS' dictionary values 
    SOUNDS['die']    = pygame.mixer.Sound('audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('audio/wing' + soundExt)

    # While loop runs until program closed
    while True:
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[0]).convert()

        IMAGES['player'] = (
            pygame.image.load('sprites/boo_up.png').convert_alpha(),
            pygame.image.load('sprites/boo_down.png').convert_alpha()
        )

        badindex = random.randint(0, len(BAD_LIST) - 1) # random obstacle sprite chosen for each game
        IMAGES['bad'] = (
            pygame.transform.flip(
                pygame.image.load(BAD_LIST[badindex]).convert_alpha(), False, True),
            pygame.image.load(BAD_LIST[badindex]).convert_alpha(),
        )

        # hitmasks for obstacles
        HITMASKS['bad'] = (
            getHitmask(IMAGES['bad'][0]),
            getHitmask(IMAGES['bad'][1]),
        )

        # hitmasks for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
        )

        # hitmasks for powerups
        HITMASKS['powerups'] = (
            getHitmask(IMAGES['powerups'][0]),
            getHitmask(IMAGES['powerups'][1]),
            getHitmask(IMAGES['powerups'][2]),
            getHitmask(IMAGES['powerups'][3])
        )

        movementInfo = showStartAnimation()
        crashInfo = gameplay(movementInfo)
        GameOverScreen(crashInfo)


def showStartAnimation():
    """ START SCREEN STATE """
    
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1])
    # iterator used to change playerIndex after every 5th iteration
    loop = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.07)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerFallVals = {'val': 0, 'dir': 1}

    high = getHighScore()

    while True: # Runs while in start screen state
        for event in pygame.event.get(): # for each user input
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit() # closes program
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                SOUNDS['wing'].play()
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
        basex = -((-basex + 3) % baseShift)
        playerFall(playerFallVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerFallVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        showHighScore(high) # displays high score on screen

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def gameplay(movementInfo):
    """ GAMEPLAY STATE """
    score = playerIndex = loop = 0 # initially sets score, player index and loop counter to 0

    # power-up values initially set to 0
    gapAdd = 0
    speedAdd = 0
    
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 obstacles
    newbad1 = getRandomBad(gapAdd)
    newbad2 = getRandomBad(gapAdd)

    # powerups
    seePower = False
    hitPower = False
    num = 0
    count = 100 
    currentPower = {}

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


    while True: # Runs while in gameplay state
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerJumpAcc
                    playerJumped = True
                    SOUNDS['wing'].play()

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
                SOUNDS['point'].play()
                

        # playerIndex basex change
        if (loop + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loop = (loop + 1) % 30
        basex = -((-basex + 3) % baseShift)
        

        # check if player collided with power up
        if seePower == True:
            hit = Hit({'x': playerx, 'y': playery, 'index': playerIndex}, currentPower, num)
            if hit == True:
                count = 0 
                hitPower = True
                seePower = False
                hitnum = num
                if num == 0:
                    score += 5
                    SOUNDS['point'].play()
                elif num == 1:
                    gapAdd += 10
                    SOUNDS['swoosh'].play()
                elif num == 2:
                    score -= 1
                    SOUNDS['die'].play()
                elif num == 3:
                    speedAdd += 5
                    SOUNDS['swoosh'].play()

        # generate power ups
        if score > 0:
            if (score % 3 == 0) and seePower == False:
                seePower = True
                num = random.randrange(0,4)
                currentPower = (getRandomPowerUp(num))
            
        # move powerup (and remove powerup if its out of the screen)
        if seePower == True and (currentPower['x'] < -IMAGES['powerups'][0].get_width()):
            currentPower = {}
            seePower = False
        elif seePower == True and (currentPower['x'] > -IMAGES['powerups'][0].get_width()) :
            currentPower['x'] += badVelX

        # stops game becoming infinitely playable   
        if gapAdd > 19:
            gapAdd = 0
            
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
            newbad = getRandomBad(gapAdd)
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

        # blits power-up icon to screen when appropriate    
        if seePower == True:
            SCREEN.blit(IMAGES['powerups'][num], (currentPower['x'], currentPower['y']))
        if count < 30:
            showMessage(hitnum)
            count += 1 


        # print score so player overlaps the score
        showScore(score)

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        
        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS+speedAdd)


def GameOverScreen(crashInfo):
    """ GAME OVER STATE """

    # uses crashInfo values
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

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    # writes player's score to text file
    file = open("Boo_HighScore.txt","a")
    scorestr = str(score)
    file.write("\n" + scorestr)
    file.close()

    newhigh = False

    # checks if new high score achieved
    high = getHighScore()
    if score >= int(high):
        newhigh = True
    
    while True: # Runs while in game over state
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
        SCREEN.blit(IMAGES['gameover'], (160, 155))
        SCREEN.blit(IMAGES['yourscore'], (20, SCREENHEIGHT * 0.1))
        
        if newhigh == True: # displays high score message if new high score achieved
            SCREEN.blit(IMAGES['newhighscore'],(90, 250))
        else:
            SCREEN.blit(IMAGES['pointsto'],(80,250))
            diff = high - score # calculates points off high score
            showDiff(diff)

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


def getRandomBad(gapAdd):
    """returns a randomly generated obstacle"""
    
    # y of gap between upper and lower obstacles
    gapY = random.randrange(0, int(BASEY * 0.6 - (BADGAPSIZE+gapAdd)))
    gapY += int(BASEY * 0.2)
    badHeight = IMAGES['bad'][0].get_height()
    badX = SCREENWIDTH + 10

    return [
        {'x': badX, 'y': gapY - badHeight},  # upper 
        {'x': badX, 'y': gapY + (BADGAPSIZE+gapAdd)}, # lower 
    ]


def getRandomPowerUp(num):
    """returns a randomly generated power up"""
    
    gapY = random.randrange(0, int(BASEY)-50)
    X = SCREENWIDTH + 10

    return {'x': X, 'y': gapY}



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

        

def showDiff(score):
    """displays the points off the high score"""
    
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset + 105, SCREENHEIGHT * 0.62))
        Xoffset += IMAGES['numbers'][digit].get_width()


def showHighScore(score):
    """displays high score"""
    
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset + 120, SCREENHEIGHT * 0.6))
        Xoffset += IMAGES['numbers'][digit].get_width()

    SCREEN.blit(IMAGES['highscore'], (Xoffset- 180, SCREENHEIGHT * 0.58))

def showMessage(num):
    """ displays power-up messages """
    
    width = IMAGES['powerupsmessages'][num].get_width()

    Xoffset = (SCREENWIDTH -width) / 2

    SCREEN.blit(IMAGES['powerupsmessages'][num], (Xoffset-10, SCREENHEIGHT * 0.88))
    

def Hit(player, currentPower, num):
    """ checks if player hit power-up """
    
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()
    playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
    powerW = IMAGES['powerups'][0].get_width()
    powerH = IMAGES['powerups'][0].get_height()

    powerRect = pygame.Rect(currentPower['x'], currentPower['y'], powerW, powerH)

    # player and powerup hitmasks
    pHitMask = HITMASKS['player'][pi]
    poHitmask = HITMASKS['powerups'][num]

    collide = pixelHit(playerRect, powerRect, pHitMask, poHitmask)

    if collide:
        return True # returns true if player and power-up have collided

def Crash(player, upperbad, lowerbad):
    """checks if player collided with obstacle or base"""
    
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
    """ checks if two objects collide and not just their rects """
    
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
    """ returns a hitmask using an image's alpha """
    
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

def getHighScore():
    """ returns high score from text file """
    
    score_list = []

    # Reads text file and appends each line to a list
    file = open("Boo_HighScore.txt","r")
    f = file.readlines()
    for line in f:
        x = int(line)
        score_list.append(x)
    file.close()

    # Insertion sort
    for index in range(1, len(score_list)):
        current = score_list[index]
        position = index

        while position > 0 and score_list[position-1] > current:
            score_list[position] = score_list[position-1]
            position -= 1

        score_list[position] = current
        
    score_list.reverse() # reverses list order so in descending

    # If more than 10 elements in list, saves only the top 10
    temp = []    
    if len(score_list) > 10:
        for z in range(0,10):
            temp.append(score_list[z])
        score_list = temp
        
    # Erases current data in text file
    file = open("Boo_HighScore.txt","w")
    file.close()

    # Writes top ten scores back into text file
    file = open("Boo_HighScore.txt","w")
    for c in range(0,(len(score_list))):
        file.write(str(score_list[c]) + "\n")
    file.write(str(score_list[(len(score_list))-1]))
    file.close()
    
    return(score_list[0]) # returns high score


if __name__ == '__main__':
    main()
