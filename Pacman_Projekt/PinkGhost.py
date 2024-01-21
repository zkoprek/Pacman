import config as c
import random
from math import floor
from Board import board
from spade.agent import Agent
from spade.template import Template
from spade.behaviour import FSMBehaviour, State
from MsgAssisant import MsgAssistant

class PinkGhost(Agent):
    class FSM(FSMBehaviour):
        async def on_start(self):
            print("PINK: Započinjem ponašanje konačnog automata.")

        async def on_end(self):
            print("PINK: Završavam ponašanje konačnog automata.")
            await self.agent.stop()

    async def setup(self):
        fsm = PinkGhost.FSM()

        fsm.add_state(name="Seek", state=PinkGhost.SeekingPacman(), initial=True)
        fsm.add_state(name="Check", state=PinkGhost.CheckingPosition())
        fsm.add_state(name="Change", state=PinkGhost.ChangingDirection())
        fsm.add_state(name="Draw", state=PinkGhost.DrawingMyself())

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
            if c.directionPink == 'UP':
                c.pinkY -= c.GHOST_SPEED
            elif c.directionPink == 'DOWN':
                c.pinkY += c.GHOST_SPEED
            elif c.directionPink == 'LEFT':
                c.pinkX -= c.GHOST_SPEED
            elif c.directionPink == 'RIGHT':
                c.pinkX += c.GHOST_SPEED
                
            # Wrap around the screen
            c.pinkX = (c.pinkX + c.WIDTH) % c.WIDTH
            c.pinkY = (c.pinkY + c.HEIGHT) % c.HEIGHT

            if c.bigDotEaten and not c.pinkAlive:
                c.screen.blit(c.deadImg, (c.pinkX-20, c.pinkY-20))
            else:
                c.screen.blit(c.pinkImg, (c.pinkX-20, c.pinkY-20))

            await self.send(MsgAssistant.createMsg(str(self.agent.jid), "main@localhost", "Nacrtao sam se"))
            self.set_next_state("Seek")

    class ChangingDirection(State): 
        async def run(self):
            if (c.canChangeDirectionPink):
                c.canChangeDirectionPink = False 

                while (not c.canGoPink):
                    c.directionPink = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
                    
                    self.currentBlockXY = PinkGhost.getCurrentBlock(c.pinkX, c.pinkY)

                    if c.determinedDirectionPink != "":
                        c.directionPink = c.determinedDirectionPink
                        c.determinedDirectionPink = ""
                    else:
                        c.directionPink = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])

                    if c.directionPink == 'UP':
                        if PinkGhost.checkDirection(self.currentBlockXY[0]-1, self.currentBlockXY[1]):
                            c.canGoPink = True
                    if c.directionPink == 'DOWN':
                        if PinkGhost.checkDirection(self.currentBlockXY[0]+1, self.currentBlockXY[1]):
                            c.canGoPink = True                                             
                    if c.directionPink == 'LEFT':
                        if PinkGhost.checkDirection(self.currentBlockXY[0], self.currentBlockXY[1]-1):
                            c.canGoPink = True
                    if c.directionPink == 'RIGHT':
                        if PinkGhost.checkDirection(self.currentBlockXY[0], self.currentBlockXY[1]+1):
                            c.canGoPink = True 

            c.canGoPink = False
            self.set_next_state("Draw") 

    class CheckingPosition(State): 
        async def run(self):          
            for intersection in c.intersectionsXY:
                if c.pinkX == intersection[0] and c.pinkY == intersection[1]:
                    c.pinkX = intersection[0]
                    c.pinkY = intersection[1]
                    c.canChangeDirectionPink = True

            if c.canChangeDirectionPink:
                self.set_next_state("Change")
            else:
                self.set_next_state("Draw")  

    class SeekingPacman(State):
        async def run(self):
            await self.receive(timeout=10)  

            self.pacmanBlockXY = PinkGhost.getCurrentBlock(c.pacmanX, c.pacmanY)
            self.pinkGhostBlockXY = PinkGhost.getCurrentBlock(c.pinkX, c.pinkY)

            self.pacmanRoundedX = round(self.pacmanBlockXY[0])
            self.ghostRoundedX = round(self.pinkGhostBlockXY[0])
            self.pacmanFlooredY = floor(self.pacmanBlockXY[1])
            self.ghostFlooredY = floor(self.pinkGhostBlockXY[1])
            self.cantSeeBlocks = [3,4,5,6,7,8,9]
            self.blocksBetween = []

            if not c.bigDotEaten:
                #Ako je Pacman iznad ghosta
                if self.pacmanFlooredY == self.ghostFlooredY and self.pacmanBlockXY[0] < self.pinkGhostBlockXY[0]:
                    for i in range (self.pacmanRoundedX + 1, self.ghostRoundedX):
                        self.blocksBetween.append(board[i][self.pacmanFlooredY])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionPink = 'UP'

                #Ako je Pacman ispod ghosta
                if self.pacmanFlooredY == self.ghostFlooredY and self.pacmanBlockXY[0] > self.pinkGhostBlockXY[0]:
                    for i in range (self.ghostRoundedX + 1, self.pacmanRoundedX):
                        self.blocksBetween.append(board[i][self.pacmanFlooredY])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionPink = 'DOWN' 

                #Ako je Pacman lijevo od ghosta
                if self.pacmanRoundedX == self.ghostRoundedX and self.pacmanBlockXY[1] < self.pinkGhostBlockXY[1]:
                    for i in range (self.pacmanFlooredY + 1, self.ghostFlooredY):
                        self.blocksBetween.append(board[self.pacmanRoundedX][i])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionPink = 'LEFT'  

                #Ako je Pacman desno od ghosta
                if self.pacmanRoundedX == self.ghostRoundedX and self.pacmanBlockXY[1] > self.pinkGhostBlockXY[1]:
                    for i in range (self.ghostFlooredY + 1, self.pacmanFlooredY):
                        self.blocksBetween.append(board[self.pacmanRoundedX][i])

                    if set(self.cantSeeBlocks).isdisjoint(self.blocksBetween):
                        c.determinedDirectionPink = 'RIGHT' 

                # Ako je došlo vrijeme za teleportaciju, tj. ako se dobila informacija od red ghosta da se pacman vidi.
                # Ali to samo ako pink ghost već ne vidi pacmana, jer bi inače moglo biti kontraproduktivno.
                if c.teleportTo != False and c.determinedDirectionPink == "":
                    print("PINK: Dobio sam informaciju da se teleportiram!")
                    c.popSound.play()
                    c.pinkX = c.WIDTH // 30 * c.teleportTo[0] 
                    c.pinkY = c.HEIGHT // 33 * c.teleportTo[1]
                    c.teleportTo = False
                    c.screen.blit(c.pinkImg, (c.pinkX-20, c.pinkY-20))          

            self.set_next_state("Check")