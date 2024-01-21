import pygame
import spade
import config as c
from spade.agent import Agent
from Pacman import Pacman
from spade.behaviour import CyclicBehaviour
from RedGhost import RedGhost
from PinkGhost import PinkGhost
from BlueGhost import BlueGhost
from OrangeGhost import OrangeGhost
from MsgAssisant import MsgAssistant
from Board import Board
from time import sleep
import os, sys

APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0]))
print("Main: ", APP_FOLDER)

pygame.display.set_caption("Python Pacman with Pygame and SPADE")

clock = pygame.time.Clock()
textFont = pygame.font.Font(os.path.join((APP_FOLDER), "emulogic.ttf"), 20)

pacman = Pacman(c.pacmanStartLoc[0], c.pacmanStartLoc[1])

redGhost = RedGhost("redGhost@localhost", "secret")
pinkGhost = PinkGhost("pinkGhost@localhost", "secret")
blueGhost = BlueGhost("blueGhost@localhost", "secret")
orangeGhost = OrangeGhost("orangeGhost@localhost", "secret")

class Referee(Agent):
    def drawText(text,font,color,x,y):
        img = font.render(text,True,color)
        c.screen.blit(img,(x,y))

    def onGhostCollision(red=False, pink=False, blue=False, orange=False, bigEatenButGhostAlive=False):
        if not c.bigDotEaten or bigEatenButGhostAlive:
            c.directionRed = ""
            c.directionPink = ""
            c.directionBlue = ""
            c.directionOrange = ""
            c.pacmanDead = True
            c.lives -= 1
        else:
            if red:
                if not c.redAlive:
                    c.ghostEatSound.play()
                    c.redAlive = True
                    c.redX, c.redY, c.directionRed = c.ghostStartLoc[0], c.ghostStartLoc[1], c.initialDirection
                else:
                    Referee.onGhostCollision(bigEatenButGhostAlive=True)
            if pink:
                if not c.pinkAlive:
                    c.ghostEatSound.play()
                    c.pinkAlive = True
                    c.pinkX, c.pinkY, c.directionPink = c.ghostStartLoc[0], c.ghostStartLoc[1], c.initialDirection
                else:
                    Referee.onGhostCollision(bigEatenButGhostAlive=True)
            if blue:
                if not c.blueAlive:
                    c.ghostEatSound.play()
                    c.blueAlive = True
                    c.blueX, c.blueY, c.directionBlue = c.ghostStartLoc[0], c.ghostStartLoc[1], c.initialDirection
                else:
                    Referee.onGhostCollision(bigEatenButGhostAlive=True)
            if orange:
                if not c.orangeAlive:
                    c.ghostEatSound.play()
                    c.orangeAlive = True
                    c.orangeX, c.orangeY, c.directionOrange = c.ghostStartLoc[0], c.ghostStartLoc[1], c.initialDirection
                else:
                    Referee.onGhostCollision(bigEatenButGhostAlive=True)

    def resetPlayers():
        c.redX, c.redY, c.directionRed = c.ghostStartLoc[0], c.ghostStartLoc[1], c.initialDirection
        c.pinkX, c.pinkY, c.directionPink = c.ghostStartLoc[0], c.ghostStartLoc[1], c.initialDirection
        c.blueX, c.blueY, c.directionBlue = c.ghostStartLoc[0], c.ghostStartLoc[1], c.initialDirection
        c.orangeX, c.orangeY, c.directionOrange = c.ghostStartLoc[0], c.ghostStartLoc[1], c.initialDirection
        c.pacmanX, c.pacmanY = c.pacmanStartLoc[0], c.pacmanStartLoc[1]
        c.pacmanDead = False

    async def setup(self):
        self.ghostBehaviour = self.RunGameBehaviour()
        self.add_behaviour(self.ghostBehaviour)

    class RunGameBehaviour(CyclicBehaviour):
        async def on_start(self):
            print("MAIN: Starting main . . .")

        async def run(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.kill()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        pacman.direction = 'UP'
                    elif event.key == pygame.K_DOWN:
                        pacman.direction = 'DOWN'
                    elif event.key == pygame.K_LEFT:
                        pacman.direction = 'LEFT'
                    elif event.key == pygame.K_RIGHT:
                        pacman.direction = 'RIGHT'
                    elif event.key == pygame.K_SPACE:
                        pacman.direction = None

            c.screen.fill(c.BLACK)

            Board.drawBoard()

            #for i in range (1, 30):
            #    pygame.draw.line(c.screen, c.RED, (c.WIDTH//30* i, 0), (c.WIDTH//30 * i, c.HEIGHT))
            #for i in range (1, 33):
            #    pygame.draw.line(c.screen, c.GREEN, (0, c.HEIGHT//33 * i), (c.WIDTH, c.HEIGHT//33 * i))    

            await self.send(MsgAssistant.createMsg(str(self.agent.jid), "redGhost@localhost", "Nacrtaj se", "inform"))
            await self.receive(timeout=10)

            await self.send(MsgAssistant.createMsg(str(self.agent.jid), "pinkGhost@localhost", "Nacrtaj se", "inform"))
            await self.receive(timeout=10)

            await self.send(MsgAssistant.createMsg(str(self.agent.jid), "blueGhost@localhost", "Nacrtaj se", "inform"))
            await self.receive(timeout=10)

            await self.send(MsgAssistant.createMsg(str(self.agent.jid), "orangeGhost@localhost", "Nacrtaj se", "inform"))
            await self.receive(timeout=10)

            # Provjera je li isteklo vrijeme kad se mogu jesti duhovi
            if pygame.time.get_ticks() - c.bigDotEatTime > 8000:
                c.bigDotEaten = False

            # Provjere za sudarom s duhovima
            if c.pacmanMask.overlap(c.redMask, (c.redX-c.pacmanX, c.redY-c.pacmanY)):
                Referee.onGhostCollision(red=True)
            if c.pacmanMask.overlap(c.pinkMask, (c.pinkX-c.pacmanX, c.pinkY-c.pacmanY)):
                Referee.onGhostCollision(pink=True)
            if c.pacmanMask.overlap(c.blueMask, (c.blueX-c.pacmanX, c.blueY-c.pacmanY)):
                Referee.onGhostCollision(blue=True)
            if c.pacmanMask.overlap(c.orangeMask, (c.orangeX-c.pacmanX, c.orangeY-c.pacmanY)):
                Referee.onGhostCollision(orange=True)

            if c.pacmanDead:
                pacman.animateDeath()
            else:
                pacman.move()

            # Provjera je li pacman pojeo pokoji dot
            if c.pacmanRect.collidelist(c.dotsRectsList) >= 0 and c.pacmanRect.collidelist(c.dotsRectsList) not in c.eatenDotsList:
                if c.pacmanRect.collidelist(c.dotsRectsList) in c.bigDotsTuple:
                    c.bigDotEaten = True
                    c.bigDotEatTime = pygame.time.get_ticks()
                    c.redAlive = False
                    c.pinkAlive = False
                    c.blueAlive = False
                    c.orangeAlive = False
                c.eatenDotsList.append(c.pacmanRect.collidelist(c.dotsRectsList))
                c.wakaSound.play()
                c.dotsEaten+=1                  

            score = str(c.dotsEaten) + "/246"
            Referee.drawText(score,textFont,c.WHITE,20,920)

            column = 0
            for _ in range (0, c.lives):
                c.screen.blit(c.lifeImg, (845-column, 917))
                column += 35

            #MsgAssistant.onMsgReceive(await self.receive(timeout=10), str(self.agent.jid))

            pygame.display.flip()

            if c.lives == 0:
                Referee.drawText("GAME OVER!",textFont,c.WHITE,350,920)
                pygame.display.flip()
                c.sirenSound.stop()
                c.deathSound.play()
                sleep(3)
                self.kill()

            if c.dotsEaten == 246:
                Referee.drawText("VICTORY!!!",textFont,c.WHITE,350,920)
                pygame.display.flip()
                c.sirenSound.stop()
                c.victorySound.play()
                sleep(6)
                self.kill()

            if not c.gameStart:
                c.gameStart = True
                c.introSound.play()
                Referee.drawText("GET READY!",textFont,c.WHITE,350,920)
                pygame.display.flip()
                sleep(5)
            
            # Jednom se pokrene zvuk za sirene i svira beskonačno dugo
            if not c.sirenSoundActive and c.gameStart:
                c.sirenSoundActive = True
                c.sirenSound.play(-1)

            if c.pacmanDead and c.lives != 0:
                c.sirenSoundActive = False
                c.introSound.stop()
                c.sirenSound.stop()
                c.deathSound.play()
                sleep(3)
                Referee.resetPlayers()
            else:
                clock.tick(60)

        async def on_end(self):
            print("MAIN: Završio sam . . .")
            await self.agent.stop()

async def main():
    main_agent = Referee("main@localhost", "secret")

    await pinkGhost.start()
    await redGhost.start()
    await blueGhost.start()
    await orangeGhost.start()
    await main_agent.start()
    await spade.wait_until_finished(main_agent)
    await redGhost.stop()
    await pinkGhost.stop()
    await blueGhost.stop()
    await orangeGhost.stop()

    MsgAssistant.printMinuses()
    print("Agenti zaustavljeni i završena igra...")

if __name__ == "__main__":
    spade.run(main())