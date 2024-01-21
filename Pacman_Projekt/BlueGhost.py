import config as c
import random
from math import floor
from Board import board, intersections
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from MsgAssisant import MsgAssistant

class BlueGhost(Agent):
    class FSM(FSMBehaviour):
        async def on_start(self):
            print("BLUE: Započinjem ponašanje konačnog automata.")

        async def on_end(self):
            print("BLUE: Završavam ponašanje konačnog automata.")
            await self.agent.stop()

    async def setup(self):
        fsm = BlueGhost.FSM()

        fsm.add_state(name="Seek", state=BlueGhost.SeekingPacman(), initial=True)
        fsm.add_state(name="Check", state=BlueGhost.CheckingPosition())
        fsm.add_state(name="Change", state=BlueGhost.ChangingDirection())
        fsm.add_state(name="Draw", state=BlueGhost.DrawingMyself())

        fsm.add_transition(source="Seek", dest="Check")
        fsm.add_transition(source="Check", dest="Change")
        fsm.add_transition(source="Check", dest="Draw")
        fsm.add_transition(source="Change", dest="Draw")
        fsm.add_transition(source="Draw", dest="Seek")

        self.add_behaviour(fsm)

    def getCurrentBlock(x,y):
        percPosX = x / c.WIDTH
        blockOnBoardX = percPosX * 30
        percPosY = y / c.HEIGHT
        blockOnBoardY = percPosY * 33
        return [blockOnBoardY, blockOnBoardX]
        
    def checkDirection(blockX, blockY):
        return board[round(blockX)][floor(blockY)] in (0, 1, 2)

    class DrawingMyself(State):
        async def run(self):
            if c.directionBlue == 'UP':
                c.blueY -= c.GHOST_SPEED
            elif c.directionBlue == 'DOWN':
                c.blueY += c.GHOST_SPEED
            elif c.directionBlue == 'LEFT':
                c.blueX -= c.GHOST_SPEED
            elif c.directionBlue == 'RIGHT':
                c.blueX += c.GHOST_SPEED
                
            # Wrap around the screen
            c.blueX = (c.blueX + c.WIDTH) % c.WIDTH
            c.blueY = (c.blueY + c.HEIGHT) % c.HEIGHT

            if c.bigDotEaten and not c.blueAlive:
                c.screen.blit(c.deadImg, (c.blueX-20, c.blueY-20))
            else:
                c.screen.blit(c.blueImg, (c.blueX-20, c.blueY-20))

            await self.send(MsgAssistant.createMsg(str(self.agent.jid), "main@localhost", "Nacrtao sam se"))
            self.set_next_state("Seek")

    class ChangingDirection(State): 
        async def run(self):
            if (c.canChangeDirectionBlue):
                c.canChangeDirectionBlue = False 

                while (not c.canGoBlue):
                    c.directionBlue = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                    
                    self.currentBlockXY = BlueGhost.getCurrentBlock(c.blueX, c.blueY)

                    if c.determinedDirectionBlue != "":
                        c.directionBlue = c.determinedDirectionBlue
                        c.lastDirectionBlue = ""
                        c.determinedDirectionBlue = ""
                    else:
                        c.directionBlue = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

                    if c.directionBlue == 'UP' and c.lastDirectionBlue != 'DOWN':
                        if BlueGhost.checkDirection(self.currentBlockXY[0]-1, self.currentBlockXY[1]):
                            c.lastDirectionBlue = 'UP'
                            c.canGoBlue = True
                    if c.directionBlue == 'DOWN' and c.lastDirectionBlue != 'UP':
                        if BlueGhost.checkDirection(self.currentBlockXY[0]+1, self.currentBlockXY[1]):
                            c.lastDirectionBlue = 'DOWN'
                            c.canGoBlue = True                                             
                    if c.directionBlue == 'LEFT' and c.lastDirectionBlue != 'RIGHT':
                        if BlueGhost.checkDirection(self.currentBlockXY[0], self.currentBlockXY[1]-1):
                            c.lastDirectionBlue = 'LEFT'
                            c.canGoBlue = True
                    if c.directionBlue == 'RIGHT' and c.lastDirectionBlue != 'LEFT':
                        if BlueGhost.checkDirection(self.currentBlockXY[0], self.currentBlockXY[1]+1):
                            c.lastDirectionBlue = 'RIGHT'
                            c.canGoBlue = True 

            c.canGoBlue = False
            self.set_next_state("Draw")  

    class CheckingPosition(State): 
        async def run(self):
            for intersection in c.intersectionsXY:
                if c.blueX == intersection[0] and c.blueY == intersection[1]:
                    c.blueX = intersection[0]
                    c.blueY = intersection[1]
                    c.canChangeDirectionBlue = True

            if c.canChangeDirectionBlue:
                self.set_next_state("Change")
            else:
                self.set_next_state("Draw")  

    class SeekingPacman(State):
        async def run(self):
            await self.receive(timeout=10)  

            self.pacmanBlockXY = BlueGhost.getCurrentBlock(c.pacmanX, c.pacmanY)
            self.blueGhostBlockXY = BlueGhost.getCurrentBlock(c.blueX, c.blueY)

            self.pacmanRoundedX = round(self.pacmanBlockXY[0])
            self.ghostRoundedX = round(self.blueGhostBlockXY[0])
            self.pacmanFlooredY = floor(self.pacmanBlockXY[1])
            self.ghostFlooredY = floor(self.blueGhostBlockXY[1])
            self.cantSeeBlocks = [3,4,5,6,7,8,9]
            self.blocksBetween = []

            if not c.bigDotEaten:
                #Ako je Pacman iznad ghosta
                if self.pacmanFlooredY == self.ghostFlooredY and self.pacmanBlockXY[0] < self.blueGhostBlockXY[0]:
                    for i in range (self.pacmanRoundedX + 1, self.ghostRoundedX):
                        self.blocksBetween.append(board[i][self.pacmanFlooredY])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionBlue = 'UP'

                #Ako je Pacman ispod ghosta
                if self.pacmanFlooredY == self.ghostFlooredY and self.pacmanBlockXY[0] > self.blueGhostBlockXY[0]:
                    for i in range (self.ghostRoundedX + 1, self.pacmanRoundedX):
                        self.blocksBetween.append(board[i][self.pacmanFlooredY])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionBlue = 'DOWN' 

                #Ako je Pacman lijevo od ghosta
                if self.pacmanRoundedX == self.ghostRoundedX and self.pacmanBlockXY[1] < self.blueGhostBlockXY[1]:
                    for i in range (self.pacmanFlooredY + 1, self.ghostFlooredY):
                        self.blocksBetween.append(board[self.pacmanRoundedX][i])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionBlue = 'LEFT'  

                #Ako je Pacman desno od ghosta
                if self.pacmanRoundedX == self.ghostRoundedX and self.pacmanBlockXY[1] > self.blueGhostBlockXY[1]:
                    for i in range (self.ghostFlooredY + 1, self.pacmanFlooredY):
                        self.blocksBetween.append(board[self.pacmanRoundedX][i])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionBlue = 'RIGHT' 

            self.set_next_state("Check")