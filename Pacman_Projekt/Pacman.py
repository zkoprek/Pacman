import pygame
import config as c
import pygame
import os, sys

APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0]))

class Pacman:
    def __init__(self, x, y):
        c.pacmanX = x
        c.pacmanY = y
        self.direction = None

    @staticmethod 
    def getCurrentBlock(x,y):
        percPosX = x / c.WIDTH
        blockOnBoardX = percPosX * 30
        percPosY = y / c.HEIGHT
        blockOnBoardY = percPosY * 33
        return [blockOnBoardY, blockOnBoardX]

    @staticmethod 
    def canPass(x,y):
        try:
            return c.screen.get_at((x, y))[0] == 0 and c.screen.get_at((x, y))[1] == 0 and c.screen.get_at((x, y))[2] == 255
        except IndexError:
            return False
        
    def animateDeath(self):
        c.screen.blit(pygame.transform.rotate(c.skullImg,0), (c.pacmanX-20, c.pacmanY-20))

    def move(self):
        if self.direction == 'UP':
            if not self.canPass(c.pacmanX, c.pacmanY-c.PACMAN_SPEED):
                c.pacmanY -= c.PACMAN_SPEED
        elif self.direction == 'DOWN':
            if not self.canPass(c.pacmanX, c.pacmanY+c.PACMAN_SPEED):
                c.pacmanY += c.PACMAN_SPEED
        elif self.direction == 'LEFT':
            if not self.canPass(c.pacmanX-c.PACMAN_SPEED, c.pacmanY):
                c.pacmanX -= c.PACMAN_SPEED
        elif self.direction == 'RIGHT':
            if not self.canPass(c.pacmanX+c.PACMAN_SPEED, c.pacmanY):
                c.pacmanX += c.PACMAN_SPEED

        # Wrap around the screen
        c.pacmanX = (c.pacmanX + c.WIDTH) % c.WIDTH
        c.pacmanY = (c.pacmanY + c.HEIGHT) % c.HEIGHT

        def loadPacmanImg():
            pacmanImg = pygame.transform.scale(pygame.image.load(os.path.join(APP_FOLDER, "Images/" + str((c.pacImgPhase % 4) +1 ) + ".png")),(40,40))
            return pacmanImg
 
        c.pacmanMask = pygame.mask.from_surface(loadPacmanImg())
        c.pacmanRect = loadPacmanImg().get_rect()

        c.pacmanRect.center = (c.pacmanX, c.pacmanY)

        if pygame.time.get_ticks() - c.lastPhaseChangeTime > 200:
            c.lastPhaseChangeTime = pygame.time.get_ticks()
            c.pacImgPhase += 1 

        if self.direction == "UP":
            c.screen.blit(pygame.transform.rotate(loadPacmanImg(),90), (c.pacmanX-20, c.pacmanY-20))   
        if self.direction == "DOWN":
            c.screen.blit(pygame.transform.rotate(loadPacmanImg(),-90), (c.pacmanX-20, c.pacmanY-20)) 
        if self.direction == "RIGHT":
            c.screen.blit(pygame.transform.rotate(loadPacmanImg(),0), (c.pacmanX-20, c.pacmanY-20))  
        if self.direction == "LEFT":
            c.screen.blit(pygame.transform.rotate(loadPacmanImg(),180), (c.pacmanX-20, c.pacmanY-20))           
        if self.direction == None:
            c.screen.blit(pygame.transform.rotate(loadPacmanImg(),0), (c.pacmanX-20, c.pacmanY-20))
        


