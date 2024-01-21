import config as c
import random
from math import floor
from Board import board, intersections
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from MsgAssisant import MsgAssistant

class OrangeGhost(Agent):
    class FSM(FSMBehaviour):
        async def on_start(self):
            print("ORANGE: Započinjem ponašanje konačnog automata.")

        async def on_end(self):
            print("ORANGE: Završavam ponašanje konačnog automata.")
            await self.agent.stop()

    async def setup(self):
        fsm = OrangeGhost.FSM()

        fsm.add_state(name="Seek", state=OrangeGhost.SeekingPacman(), initial=True)
        fsm.add_state(name="Check", state=OrangeGhost.CheckingPosition())
        fsm.add_state(name="Change", state=OrangeGhost.ChangingDirection())
        fsm.add_state(name="Draw", state=OrangeGhost.DrawingMyself())

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
            if c.directionOrange == 'UP':
                c.orangeY -= c.GHOST_SPEED
            elif c.directionOrange == 'DOWN':
                c.orangeY += c.GHOST_SPEED
            elif c.directionOrange == 'LEFT':
                c.orangeX -= c.GHOST_SPEED
            elif c.directionOrange == 'RIGHT':
                c.orangeX += c.GHOST_SPEED
                
            # Wrap around the screen
            c.orangeX = (c.orangeX + c.WIDTH) % c.WIDTH
            c.orangeY = (c.orangeY + c.HEIGHT) % c.HEIGHT

            if c.bigDotEaten and not c.orangeAlive:
                c.screen.blit(c.deadImg, (c.orangeX-20, c.orangeY-20))
            else:
                c.screen.blit(c.orangeImg, (c.orangeX-20, c.orangeY-20))

            await self.send(MsgAssistant.createMsg(str(self.agent.jid), "main@localhost", "Nacrtao sam se"))
            self.set_next_state("Seek")   

    class ChangingDirection(State): 
        async def run(self):
            if (c.canChangeDirectionOrange):
                c.canChangeDirectionOrange = False 

                while (not c.canGoOrange):
                    c.directionOrange = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                    
                    self.currentBlockXY = OrangeGhost.getCurrentBlock(c.orangeX, c.orangeY)

                    if c.determinedDirectionOrange != "":
                        c.directionOrange = c.determinedDirectionOrange
                        c.lastDirectionOrange = ""
                        c.determinedDirectionOrange = ""
                    else:
                        c.directionOrange = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

                    if c.directionOrange == 'UP' and c.lastDirectionOrange != 'DOWN':
                        if OrangeGhost.checkDirection(self.currentBlockXY[0]-1, self.currentBlockXY[1]):
                            c.lastDirectionOrange = 'UP'
                            c.canGoOrange = True
                    if c.directionOrange == 'DOWN' and c.lastDirectionOrange != 'UP':
                        if OrangeGhost.checkDirection(self.currentBlockXY[0]+1, self.currentBlockXY[1]):
                            c.lastDirectionOrange = 'DOWN'
                            c.canGoOrange = True                                             
                    if c.directionOrange == 'LEFT' and c.lastDirectionOrange != 'RIGHT':
                        if OrangeGhost.checkDirection(self.currentBlockXY[0], self.currentBlockXY[1]-1):
                            c.lastDirectionOrange = 'LEFT'
                            c.canGoOrange = True
                    if c.directionOrange == 'RIGHT' and c.lastDirectionOrange != 'LEFT':
                        if OrangeGhost.checkDirection(self.currentBlockXY[0], self.currentBlockXY[1]+1):
                            c.lastDirectionOrange = 'RIGHT'
                            c.canGoOrange = True 

            c.canGoOrange = False
            self.set_next_state("Draw")      
    
    class CheckingPosition(State): 
        async def run(self):
            for intersection in c.intersectionsXY:
                if c.orangeX == intersection[0] and c.orangeY == intersection[1]:
                    c.orangeX = intersection[0]
                    c.orangeY = intersection[1]
                    c.canChangeDirectionOrange = True

            if c.canChangeDirectionOrange:
                self.set_next_state("Change")
            else:
                self.set_next_state("Draw")  

    class SeekingPacman(State):
        async def run(self):
            await self.receive(timeout=10)  

            self.pacmanBlockXY = OrangeGhost.getCurrentBlock(c.pacmanX, c.pacmanY)
            self.orangeGhostBlockXY = OrangeGhost.getCurrentBlock(c.orangeX, c.orangeY)

            self.pacmanRoundedX = round(self.pacmanBlockXY[0])
            self.ghostRoundedX = round(self.orangeGhostBlockXY[0])
            self.pacmanFlooredY = floor(self.pacmanBlockXY[1])
            self.ghostFlooredY = floor(self.orangeGhostBlockXY[1])
            self.cantSeeBlocks = [3,4,5,6,7,8,9]
            self.blocksBetween = []

            if not c.bigDotEaten:
                #Ako je Pacman iznad ghosta
                if self.pacmanFlooredY == self.ghostFlooredY and self.pacmanBlockXY[0] < self.orangeGhostBlockXY[0]:
                    for i in range (self.pacmanRoundedX + 1, self.ghostRoundedX):
                        self.blocksBetween.append(board[i][self.pacmanFlooredY])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionOrange = 'UP'

                #Ako je Pacman ispod ghosta
                if self.pacmanFlooredY == self.ghostFlooredY and self.pacmanBlockXY[0] > self.orangeGhostBlockXY[0]:
                    for i in range (self.ghostRoundedX + 1, self.pacmanRoundedX):
                        self.blocksBetween.append(board[i][self.pacmanFlooredY])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionOrange = 'DOWN' 

                #Ako je Pacman lijevo od ghosta
                if self.pacmanRoundedX == self.ghostRoundedX and self.pacmanBlockXY[1] < self.orangeGhostBlockXY[1]:
                    for i in range (self.pacmanFlooredY + 1, self.ghostFlooredY):
                        self.blocksBetween.append(board[self.pacmanRoundedX][i])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionOrange = 'LEFT'  

                #Ako je Pacman desno od ghosta
                if self.pacmanRoundedX == self.ghostRoundedX and self.pacmanBlockXY[1] > self.orangeGhostBlockXY[1]:
                    for i in range (self.ghostFlooredY + 1, self.pacmanFlooredY):
                        self.blocksBetween.append(board[self.pacmanRoundedX][i])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionOrange = 'RIGHT'        

            self.set_next_state("Check")