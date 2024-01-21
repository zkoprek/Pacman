import config as c
import random
import pygame
from math import floor
from Board import board, intersections
from spade.agent import Agent
from spade.template import Template
from spade.behaviour import CyclicBehaviour
from MsgAssisant import MsgAssistant

class RedGhost(Agent):
    async def setup(self):   
        ghostBehaviour = self.PlayGameBehaviour()
        template = Template(metadata={"ontology": "inform"})
        self.add_behaviour(ghostBehaviour, template)

    def getCurrentBlock(x, y):
        percPosX = x / c.WIDTH
        blockOnBoardX = percPosX * 30
        percPosY = y / c.HEIGHT
        blockOnBoardY = percPosY * 33
        return [blockOnBoardY, blockOnBoardX]
        
    def checkDirection(blockX, blockY):
        return board[round(blockX)][floor(blockY)] in (0, 1, 2)   

    class PlayGameBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("RED: Starting behaviour ghost. . .")   

        def move(self):
            #Poklapa li se srediste ghosta s intersectionom, omoguci se ulaz u iduci if()
            if c.firstRun:
                for intersection in intersections:  
                    c.firstRun = False
                    c.intersectionsXY.append([c.WIDTH // 30 * intersection[0], c.HEIGHT // 33 * intersection[1]])           
            
            for intersection in c.intersectionsXY:
                if c.redX == intersection[0] and c.redY == intersection[1]:
                    c.redX = intersection[0]
                    c.redY = intersection[1]
                    c.canChangeDirectionRed = True
        
            if (c.canChangeDirectionRed):
                c.canChangeDirectionRed = False 

                while (not c.canGoRed):

                    if c.determinedDirectionRed != "":
                        c.directionRed = c.determinedDirectionRed
                        c.lastDirectionRed = ""
                        c.determinedDirectionRed = ""
                    else:
                        c.directionRed = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                        
                    self.currentBlockXY = RedGhost.getCurrentBlock(c.redX, c.redY)

                    if c.directionRed == 'UP' and c.lastDirectionRed != 'DOWN':
                        if RedGhost.checkDirection(self.currentBlockXY[0]-1, self.currentBlockXY[1]):
                            c.lastDirectionRed = 'UP'
                            c.canGoRed = True 
                    if c.directionRed == 'DOWN' and c.lastDirectionRed != 'UP':
                        if RedGhost.checkDirection(self.currentBlockXY[0]+1, self.currentBlockXY[1]):
                            c.lastDirectionRed = 'DOWN'  
                            c.canGoRed = True                                        
                    if c.directionRed == 'LEFT' and c.lastDirectionRed != 'RIGHT':
                        if RedGhost.checkDirection(self.currentBlockXY[0], self.currentBlockXY[1]-1):
                            c.lastDirectionRed = 'LEFT'
                            c.canGoRed = True 
                    if c.directionRed == 'RIGHT' and c.lastDirectionRed != 'LEFT':
                        if RedGhost.checkDirection(self.currentBlockXY[0], self.currentBlockXY[1]+1):
                            c.lastDirectionRed = 'RIGHT'
                            c.canGoRed = True 

            c.canGoRed = False  

            if c.directionRed == 'UP':
                c.redY -= c.GHOST_SPEED
            elif c.directionRed == 'DOWN':
                c.redY += c.GHOST_SPEED
            elif c.directionRed == 'LEFT':
                c.redX -= c.GHOST_SPEED
            elif c.directionRed == 'RIGHT':
                c.redX += c.GHOST_SPEED
                
            # Wrap around the screen
            c.redX = (c.redX + c.WIDTH) % c.WIDTH
            c.redY = (c.redY + c.HEIGHT) % c.HEIGHT

            if c.bigDotEaten and not c.redAlive:
                c.screen.blit(c.deadImg, (c.redX-20, c.redY-20))
            else:
                c.screen.blit(c.redImg, (c.redX-20, c.redY-20))

        def tellPink(self):
            if pygame.time.get_ticks() - c.lastTeleportUsed > 10000:

                # Ovdje se racuna koje je mjesto za teleportaciju duha najblize pacmanu. Teleportirati se moze najcesce svakih 10 sekundi.
                if abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[0] - 22.5) < abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[0] - 7.5) and\
                    abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[1] - 24.5) < abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[1] - 6.5):
                    c.teleportTo = [22.5,24.5]
                if abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[0] - 22.5) > abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[0] - 7.5) and\
                    abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[1] - 24.5) < abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[1] - 6.5):
                    c.teleportTo = [22.5,6.5]
                if abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[0] - 22.5) < abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[0] - 7.5) and\
                    abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[1] - 24.5) > abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[1] - 6.5):
                    c.teleportTo = [7.5,24.5]
                if abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[0] - 22.5) > abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[0] - 7.5) and\
                    abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[1] - 24.5) > abs(RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)[1] - 6.5):
                    c.teleportTo = [7.5,6.5]

                print("RED: Pink, teleportiraj se!")
                c.lastTeleportUsed = pygame.time.get_ticks()
            else: 
                return

        async def run(self):
            await self.receive(timeout=10)

            self.pacmanBlockXY = RedGhost.getCurrentBlock(c.pacmanX, c.pacmanY)
            self.redGhostBlockXY = RedGhost.getCurrentBlock(c.redX, c.redY)

            self.pacmanRoundedX = round(self.pacmanBlockXY[0])
            self.ghostRoundedX = round(self.redGhostBlockXY[0])
            self.pacmanFlooredY = floor(self.pacmanBlockXY[1])
            self.ghostFlooredY = floor(self.redGhostBlockXY[1])
            self.cantSeeBlocks = [3,4,5,6,7,8,9]
            self.blocksBetween = []

            if not c.bigDotEaten:
                #Ako je Pacman iznad ghosta
                if self.pacmanFlooredY == self.ghostFlooredY and self.pacmanBlockXY[0] < self.redGhostBlockXY[0]:
                    for i in range (self.pacmanRoundedX + 1, self.ghostRoundedX):
                        self.blocksBetween.append(board[i][self.pacmanFlooredY])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionRed = 'UP'
                        self.tellPink()

                #Ako je Pacman ispod ghosta
                if self.pacmanFlooredY == self.ghostFlooredY and self.pacmanBlockXY[0] > self.redGhostBlockXY[0]:
                    for i in range (self.ghostRoundedX + 1, self.pacmanRoundedX):
                        self.blocksBetween.append(board[i][self.pacmanFlooredY])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionRed = 'DOWN' 
                        self.tellPink()

                #Ako je Pacman lijevo od ghosta
                if self.pacmanRoundedX == self.ghostRoundedX and self.pacmanBlockXY[1] < self.redGhostBlockXY[1]:
                    for i in range (self.pacmanFlooredY + 1, self.ghostFlooredY):
                        self.blocksBetween.append(board[self.pacmanRoundedX][i])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionRed = 'LEFT' 
                        self.tellPink() 

                #Ako je Pacman desno od ghosta
                if self.pacmanRoundedX == self.ghostRoundedX and self.pacmanBlockXY[1] > self.redGhostBlockXY[1]:
                    for i in range (self.ghostFlooredY + 1, self.pacmanFlooredY):
                        self.blocksBetween.append(board[self.pacmanRoundedX][i])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionRed = 'RIGHT' 
                        self.tellPink()                 
            
            self.move()

            await self.send(MsgAssistant.createMsg(str(self.agent.jid), "main@localhost", "Nacrtao sam se"))