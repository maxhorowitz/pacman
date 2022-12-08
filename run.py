import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
from sprites import LifeSprites
from sprites import MazeSprites
from mazedata import MazeData
import sys
import random
from math import inf

PACMAN_AGENT = 0
BLINKY_AGENT = 1
PINKY_AGENT = 2
INKY_AGENT = 3
CLYDE_AGENT = 4

ghost_modedict = {
    SCATTER : "scatter",
    CHASE : "chase",
    FREIGHT : "freight",
    SPAWN : "spawn",
}

agentdict = {
    PACMAN_AGENT:"pacman",
    BLINKY_AGENT: "blinky",
    PINKY_AGENT: "pinky",
    INKY_AGENT: "inky",
    CLYDE_AGENT: "clyde",
}

directiondict = {
    STOP:"stop",
    UP:"up",
    DOWN:"down",
    LEFT:"left",
    RIGHT:"right",
    PORTAL:"portal",
}

MAX_DEPTH = 5
DEBUG = True

def debug(message):
    if DEBUG:
        print(message)

class Gamestate:
    def __init__(self, dt, pacmanPosition, ghostPositions, pelletPositions, validActionsList):
        self.dt = dt
        self.pacmanPosition = pacmanPosition
        self.ghostPositions = ghostPositions
        self.pelletPositions = pelletPositions
        self.validActionsList = validActionsList
        self._id = random.randint(0,9999999)

    def printGamestate(self):
        print("\n--------"+str(self._id)+"--------")
        print()
        print(self.dt)
        print()
        print(self.pacmanPosition)
        print()
        print(self.ghostPositions)
        print()
        print(self.pelletPositions)
        print()
        print(self.validActionsList)
        print()
        print("--------"+str(self._id)+"--------\n")

    def getDt(self):
        return self.dt

    def setDt(self, dt):
        self.dt = dt
    
    def getPacmanPosition(self):
        return self.pacmanPosition

    def modifyPacmanPosition(self, pacmanPosition):
        self.pacmanPosition = pacmanPosition

    def getGhostPositions(self):
        return self.ghostPositions

    def modifyGhostPositions(self, agent, agentValidPosition):
        self.ghostPositions[agent] = agentValidPosition

    def getPelletPositions(self):
        return self.pelletPositions

    def modifyPelletPositions(self, pellet):
        if pellet is not None:
            self.pelletPositions.remove(pellet)

    def getValidActionsList(self):
        return self.validActionsList

    def modifyValidActionsList(self, agent, agentValidActions):
        self.validActionsList[agent] = agentValidActions

class GameController(object):
    def __init__(self, isAi):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.mazedata = MazeData()
        self.isAi = (isAi == "ai")
        self.minimaxDepth = 2 if self.isAi else None
        self._hash = random.randint(0000000, 9999999)

    def getHash(self):
        return self._hash

    def setBackground(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, self.level%5)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(self.mazedata.obj.name+".txt", self.mazedata.obj.name+"_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name+".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart))
        self.pellets = PelletGroup(self.mazedata.obj.name+".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)

        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def startGame_old(self):      
        self.mazedata.loadMaze(self.level)#######
        self.mazesprites = MazeSprites("maze1.txt", "maze1_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0,17), (27,17))
        homekey = self.nodes.createHomeNodes(11.5, 14)
        self.nodes.connectHomeNodes(homekey, (12,14), LEFT)
        self.nodes.connectHomeNodes(homekey, (15,14), RIGHT)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(15, 26))
        self.pellets = PelletGroup("maze1.txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 0+14))
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(0+11.5, 3+14))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(4+11.5, 3+14))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, LEFT, self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, RIGHT, self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.nodes.denyAccessList(12, 14, UP, self.ghosts)
        self.nodes.denyAccessList(15, 14, UP, self.ghosts)
        self.nodes.denyAccessList(12, 26, UP, self.ghosts)
        self.nodes.denyAccessList(15, 26, UP, self.ghosts)

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.ghosts.update(dt)      
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()
        bestDirection = None
        if self.pacman.alive:
            if not self.pause.paused:
                if self.isAi == True:
                    bestDirection = self.ai(dt)
                self.pacman.update(dt, bestDirection)
        else:
            self.pacman.update(dt, bestDirection)
        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.textgroup.hideText()
                            self.showEntities()
                        else:
                            self.textgroup.showText(PAUSETXT)
                            #self.hideEntities()
    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)                  
                    self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -=  1
                        self.lifesprites.removeImage()
                        self.pacman.die()               
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)
    
    def checkFruitEvents(self):
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)

    def render(self):
        self.screen.blit(self.background, (0, 0))
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i+1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))

        pygame.display.update()

    def initializeGamestate(self, dt):
        pacmanPosition = self.pacman.position
        ghostPositions = []
        pelletPositions = []
        validActionsList = [self.pacman.validDirections(),]
        for ghost in self.ghosts.ghosts:
            validActionsList.append(ghost.validDirections())
            ghostPositions.append(ghost.position)
        for pellet in self.pellets.pelletList:
            pelletPositions.append(pellet)
        for powerpellet in self.pellets.powerpellets:
            pelletPositions.append(powerpellet)
        return Gamestate(dt, pacmanPosition, ghostPositions, pelletPositions, validActionsList)

    def successorGamestate(self, gs, agent, agentDirection):

        if agent == PACMAN_AGENT:
            # modify pacman position
            customPosition = self.pacman.customPosition(gs.getPacmanPosition(), agentDirection, gs.getDt())
            gs.modifyPacmanPosition(customPosition)

            # modify the valid actions list
            validDirectionsFromCustomPosition = self.pacman.validDirectionsBySimulatedPosition(customPosition)
            gs.modifyValidActionsList(agent, validDirectionsFromCustomPosition)

            # modify pellet positions if pacman ate any of them
            gs.modifyPelletPositions(self.pacman.simulationPacmanCollideWithPelletsCheck(gs.getPacmanPosition(), gs.getPelletPositions()))

        elif agent in [BLINKY_AGENT, PINKY_AGENT, INKY_AGENT, CLYDE_AGENT]:
            ghost = self.ghosts.ghosts[agent-1]

            # modify ghost position
            customPosition = ghost.customPosition(ghost.position, agentDirection, gs.getDt())
            gs.modifyGhostPositions(agent-1,customPosition)

            # modify the valid actions list
            validDirectionsFromCustomPosition = ghost.validDirectionsBySimulatedPosition(customPosition)
            gs.modifyValidActionsList(agent, validDirectionsFromCustomPosition)
        else:
            raise Exception("Agent index out of bounds!")
        return gs

    def ai(self, dt):
        gs = self.initializeGamestate(dt)
        return self.minimax(gs, 0, 0, -inf, inf)[1]

    def heuristic(self, gs):

        def manhattan(posA, posB):
            return abs(posA.x - posB.x) + abs(posA.y - posB.y)

        closestGhostImportance = 1
        if self.ghosts.ghosts[0].mode.current is FREIGHT:
            closestGhostImportance *= 100
        else:
            closestGhostImportance *= -30
        def closestGhost(gs):
            pacmanPos = gs.getPacmanPosition()
            ghostPositions = gs.getGhostPositions()
            closestGhost, distanceToClosestGhost = None, None
            for i in range(0, len(ghostPositions)):
                d = manhattan(pacmanPos, ghostPositions[i])
                if closestGhost is None or distanceToClosestGhost > d:
                    closestGhost = (i+1)
                    distanceToClosestGhost = d
            return closestGhost, distanceToClosestGhost

        proximityToPelletsImportance = 5
        def proximityToPellets(gs):
            pacmanPos = gs.getPacmanPosition()
            pelletPositions = gs.getPelletPositions()
            proximity = 0
            for pellet in pelletPositions:
                if pellet.name == PELLET:
                    d = manhattan(pacmanPos, pellet.position)
                    if d < 5:
                        proximity += (100 / d)
                    elif d < 10:
                        proximity += (50 / d)
                    elif d < 25:
                        proximity += (20 / d)
                    elif d < 50:
                        proximity += (10 / d)
                    elif d < 75:
                        proximity += (6.67 / d)
                    elif d < 100:
                        proximity += (5 / d)
                elif pellet.name == POWERPELLET:
                    d = manhattan(pacmanPos, pellet.position)
                    if d < 5:
                        proximity += 10*(100 / d)
                    elif d < 10:
                        proximity += 10*(50 / d)
                    elif d < 25:
                        proximity += 10*(20 / d)
                    elif d < 50:
                        proximity += 10*(10 / d)
                    elif d < 75:
                        proximity += 10*(6.67 / d)
                    elif d < 100:
                        proximity += 10*(5 / d)
            return proximity

        evalGamestate = 0
        evalGamestate += (closestGhost(gs)[1]) * closestGhostImportance
        evalGamestate += (proximityToPellets(gs)) * proximityToPelletsImportance
        return evalGamestate

    def _minimax_debug(self, gs, depth, agent, alpha, beta):
        if DEBUG:
            print("\n-------- GS: "+str(gs._id)+" --------")
            if agent == PACMAN_AGENT:
                pacPos = str(gs.getPacmanPosition())
                print("@@ pacman @@")
                print("Maximizing for pacman at position="+pacPos)
            elif agent == BLINKY_AGENT:
                blinkyPos = str(gs.getGhostPositions()[agent-1])
                print("@@ blinky @@")
                print("Minimizing for blinky at position="+blinkyPos)
            elif agent == PINKY_AGENT:
                pinkyPos = str(gs.getGhostPositions()[agent-1])
                print("@@ pinky @@")
                print("Minimizing for pinky at position="+pinkyPos)
            elif agent == INKY_AGENT:
                inkyPos = str(gs.getGhostPositions()[agent-1])
                print("@@ inky @@")
                print("Minimizing for inky at position="+inkyPos)
            elif agent == CLYDE_AGENT:
                clydePos = str(gs.getGhostPositions()[agent-1])
                print("@@ clyde @@")
                print("Minimizing for clyde at position="+clydePos)
            else:
                raise Exception("This should not happen.")
            print("Minimax info: depth="+str(depth)+", alpha="+str(alpha)+", beta="+str(beta))
            print("-------- GS: "+str(gs._id)+" --------\n")

    def _selection_debug(self, action, val, mode):
        s = "Move pacman "+directiondict[action]+", with heuristic="+str(val)+", ghosts_mode="+ghost_modedict[mode]
        debug(str(s))

    def minimax(self, gs, depth, agent, alpha, beta):

        if agent == -1:
            depth += 1
            agent = 0

        if depth == MAX_DEPTH:
            return self.heuristic(gs), None

        bestVal, bestAction = None, None

        if agent == PACMAN_AGENT:

            for action in gs.getValidActionsList()[agent]:
                
                next_gs = self.successorGamestate(gs, agent, action)

                val, _ = self.minimax(next_gs, depth, agent+1, alpha, beta)

                if bestVal is None or val > bestVal:
                    bestVal, bestAction = val, action

                alpha = max(alpha, val)

                if beta < alpha:
                    break

        elif agent in [BLINKY_AGENT, PINKY_AGENT, INKY_AGENT, CLYDE_AGENT]:

            for action in gs.getValidActionsList()[agent]:

                next_gs = self.successorGamestate(gs, agent, action)

                val = None
                if agent is CLYDE_AGENT:
                    val, _ = self.minimax(next_gs, depth, -1, alpha, beta)
                else:
                    val, _ = self.minimax(next_gs, depth, agent+1, alpha, beta)
                assert val is not None

                if  bestVal is None or val < bestVal:
                    bestVal, bestAction = val, action

                beta = min(beta, val)

                if beta < alpha:
                    break

        else:

            raise Exception("This shouldn't happen!")

        if bestVal is None:
            return self.heuristic(gs), None

        self._selection_debug(bestAction, bestVal, self.ghosts.ghosts[0].mode.current)

        return bestVal, bestAction

if __name__ == "__main__":
    gameMode = str(sys.argv[1])
    game = GameController(gameMode)
    game.startGame()
    while True:
        game.update()



