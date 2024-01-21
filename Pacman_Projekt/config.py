import pygame
import os, sys

APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0]))
print(APP_FOLDER)

pygame.mixer.init(44100, -16, 2, 512)
pygame.init()

# Constants
WIDTH, HEIGHT = 900, 950
GRID_SIZE = 30
PACMAN_RADIUS = 18
GHOST_RADIUS = 18
PACMAN_SPEED = 2
GHOST_SPEED = 1

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255,192,203)
GREEN = (0,255,0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Images
lastPhaseChangeTime = 0
pacImgPhase = 1
pacmanRect = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/1.png")),(40,40)).get_rect()
pacmanMask = pygame.mask.from_surface(pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/1.png")),(40,40)))

skullImg = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/skull.png")),(40,40))

redImg = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/red.png")),(40,40))
redMask = pygame.mask.from_surface(redImg)

pinkImg = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/pink.png")),(40,40))
pinkMask = pygame.mask.from_surface(pinkImg)

blueImg = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/blue.png")),(40,40))
blueMask = pygame.mask.from_surface(blueImg)

orangeImg = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/orange.png")),(40,40))
orangeMask = pygame.mask.from_surface(orangeImg)

deadImg = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/dead.png")),(40,40))
deadMask = pygame.mask.from_surface(deadImg)

lifeImg = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/life.png")),(30,30))

dotsRectsList = []
dotsCoordinates = []
dotsEaten = 0
dotsOverall = 242
firstRun = True
eatenDotsList = []
bigDotsTuple = (30,35,158,179)

bigDotEaten = False
bigDotEatTime = 0

# Variables for moving ghosts RANDOMLY
ghostStartLoc = [WIDTH // 30 * 15, HEIGHT // 33 * 14.5]
initialDirection = "UP"
intersectionsXY = []

redX = ghostStartLoc[0]
redY = ghostStartLoc[1]
pinkX = ghostStartLoc[0]
pinkY = ghostStartLoc[1]
blueX = ghostStartLoc[0]
blueY = ghostStartLoc[1]
orangeX = ghostStartLoc[0]
orangeY = ghostStartLoc[1]

directionRed = initialDirection
lastDirectionRed = ""
canChangeDirectionRed = False
canGoRed = False
redAlive = True

directionPink = initialDirection
canChangeDirectionPink = False
lastDirectionPink = ""
canGoPink = False
pinkAlive = True

directionBlue = initialDirection
canChangeDirectionBlue = False
lastDirectionBlue = ""
canGoBlue = False
blueAlive = True

directionOrange = initialDirection
canChangeDirectionOrange = False
lastDirectionOrange = ""
canGoOrange = False
orangeAlive = True

# Variables for seeking pacman
pacmanX = ""
pacmanY = ""
determinedDirectionRed = ""
determinedDirectionPink = ""
determinedDirectionBlue = ""
determinedDirectionOrange = ""

# Variables for hunting once pacman is spotted
teleportTo = False
lastTeleportUsed = 0

# Variables for life reset / game over
pacmanDead = False
pacmanStartLoc = [WIDTH // 30 * 15, int(HEIGHT // 33 * 18.5)]
lives = 3

# Variables for sound
gameStart = False
sirenSoundActive = False
introSound = pygame.mixer.Sound(os.path.join(APP_FOLDER, "Sounds/intro.mp3"))
deathSound = pygame.mixer.Sound(os.path.join(APP_FOLDER, "Sounds/death.mp3"))
wakaSound = pygame.mixer.Sound(os.path.join(APP_FOLDER, "Sounds/waka.mp3"))
wakaSound.set_volume(0.4)
sirenSound = pygame.mixer.Sound(os.path.join(APP_FOLDER, "Sounds/siren.mp3"))
sirenSound.set_volume(0.3)
popSound = pygame.mixer.Sound(os.path.join(APP_FOLDER, "Sounds/pop.mp3"))
ghostEatSound = pygame.mixer.Sound(os.path.join(APP_FOLDER, "Sounds/ghostEat.mp3"))
victorySound = pygame.mixer.Sound(os.path.join(APP_FOLDER, "Sounds/victory.mp3"))

