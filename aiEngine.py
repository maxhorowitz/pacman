from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup, Ghost, copy
from fruit import Fruit
from constants import *
from entity import Entity
from pacman import Pacman, copy


from random import randint, choice
from math import inf

MAX_DEPTH = 2
DEBUG = True

class Gamestate(object):
    def __init__(self, clock, pacman, ghosts, pellets, fruit, level, lives, score):
        self._id = randint(1000000000, 9999999999)
        self.clock = clock
        self.pacman = copy(pacman)
        self.ghosts = copy(ghosts)
        self.pellets = pellets
        self.fruit = fruit
        self.level = level
        self.lives = lives
        self.score = score

    def id(self):
        return self._id

    def movePacman(self, dt, direction):
        self.pacman.position += self.pacman.directions[direction]*self.pacman.speed*dt
        if self.pacman.overshotTarget():
            self.pacman.node = self.pacman.target
            if self.pacman.node.neighbors[PORTAL] is not None:
                self.pacman.node = self.pacman.node.neighbors[PORTAL]
            self.pacman.target = self.pacman.getNewTarget(direction)
            if self.pacman.target is not self.pacman.node:
                self.pacman.direction = direction
            else:
                self.pacman.target = self.pacman.getNewTarget(self.pacman.direction)
            if self.pacman.target is self.pacman.node:
                self.pacman.direction = STOP
            self.pacman.setPosition()
        else: 
            if self.pacman.oppositeDirection(direction):
                self.pacman.reverseDirection()

    def moveGhosts(self, dt):
        for ghost in self.ghosts:
            ghost.mode.update(dt)
            if ghost.mode.current is SCATTER:
                ghost.scatter()
            elif ghost.mode.current is CHASE:
                ghost.chase()
            ghost.position += ghost.directions[ghost.direction]*ghost.speed*dt
            if ghost.overshotTarget():
                ghost.node = ghost.target
                directions = ghost.validDirections()
                direction = ghost.directionMethod(directions)
                if not ghost.disablePortal:
                    if ghost.node.neighbors[PORTAL] is not None:
                        ghost.node = ghost.node.neighbors[PORTAL]
                ghost.target = ghost.getNewTarget(direction)
                if ghost.target is not ghost.node:
                    ghost.direction = direction
                else:
                    ghost.target = ghost.getNewTarget(ghost.direction)
                ghost.setPosition()

    def updatePellets(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.score += pellet.points
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
    
    def updateGhosts(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.score += ghost.points
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -=  1
        
    def updateFruits(self):
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.score += self.fruit.points

    def nextGamestate(self, pacmanDirection):
        # assert pacmanDirection in self.pacman.validDirections()
        dt = self.clock.tick(30) / 1000.0
        copy = Gamestate(self.clock, self.pacman, self.ghosts, self.pellets, self.fruit, self.level, self.lives, self.score)
        copy.movePacman(dt, pacmanDirection)
        copy.moveGhosts(dt)
        copy.updatePellets()
        copy.updateGhosts()
        copy.updateFruits()
        return copy
    
    def successorGamestates(self):
        successors = []
        successor = None
        for direction in self.pacman.validDirections():
            successor = self.nextGamestate(direction)
            successors.append(successor)
        return successors

    def heuristic(self):
        return self.lives*self.score

def aiEngine(clock, pacman, ghosts, pellets, fruit, level, lives, score):
    ret = None
    gamestate = Gamestate(clock, pacman, ghosts, pellets, fruit, level, lives, score)

    # ----------- MINIMAX -----------
    ret = minimax_helper(gamestate)

    # ----------- RANDOM ------------
    # ret = random(gamestate)

    # ------- NO TURNING BACK -------
    # ret = noTurningBack(gamestate)

    # ----------- GREEDY ------------
    # ret = greedy(gamestate)
    return ret

# ---------------------------
# --------- MINIMAX ---------
# ---------------------------

def minimax_helper(current):
    h, next = minimax(current, 0, True, -inf, inf)
    print("Selected gamestate id", str(next.id()), "with value", str(h))
    return next.pacman.direction

def minimax(gamestate, depth, isMaximizingPlayer, alpha, beta):
    if depth == MAX_DEPTH:
        return gamestate.heuristic(), gamestate
    if isMaximizingPlayer:
        bestVal = -inf
        bestSuccessor = None
        successors = gamestate.successorGamestates()
        for successorGamestate in successors:
            value, successor = minimax(successorGamestate, depth+1, False, alpha, beta)
            if value > bestVal:
                bestVal, bestSuccessor = value, successor
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestSuccessor
    else:
        bestVal = inf
        bestSuccessor = None
        successors = gamestate.successorGamestates()
        for successorGamestate in successors:
            value, successor = minimax(successorGamestate, depth+1, True, alpha, beta)
            if value < bestVal:
                bestVal, bestSuccessor = value, successor
            beta = min(beta, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestSuccessor

# ------------------------------
# ---------  RANDOM   ----------
# ------------------------------

def random(current):
    currentDirection = current.pacman.direction
    while current.pacman.alive:
        if currentDirection in current.pacman.validDirections():
            return currentDirection
        else:
            validDirections = current.pacman.validDirections()
            return choice(validDirections)

# ------------------------------
# ------- NO TURNING BACK ------
# ------------------------------

def noTurningBack(current):
    recentDirection = current.pacman.recentDirection
    while current.pacman.alive:
        validDirections = current.pacman.validDirections()
        try:
            validDirections.remove(recentDirection * -1)
        except ValueError:
            pass
        return choice(validDirections)

# ------------------------------
# ---------  GREEDY   ----------
# ------------------------------

def greedy(current):
    successorGamestates = current.successorGamestates()
    max = 0
    bestSuccessorGamestate = current
    for successor in successorGamestates:
        if successor.heuristic() > max:
            max = successor.heuristic()
            bestSuccessorGamestate = successor
            message = "Gamestate",successor.id(),"with value",max
            debug(message)
    return bestSuccessorGamestate.pacman.direction


# ---- DEBUG CONSOLE OUTPUT ----
def debug(message):
    if DEBUG:
        print(message)