from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from constants import *
from pacman import Pacman

from random import randint
from math import inf

MAX_DEPTH = 3

class GameState(object):
    def __init__(self, clock, pacman, fruit, level, lives, score, nodes, pellets, ghosts, mazedata, fruitCaptured):
        self.clock = clock
        self.pacman = pacman
        self.fruit = fruit
        self.level = level
        self.lives = lives
        self.score = score
        self.nodes = nodes
        self.pellets = pellets
        self.ghosts = ghosts
        self.fruitCaptured = fruitCaptured
        self.mazedata = mazedata

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.score += pellet.points
    
    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.score += ghost.points
                    self.ghosts.updatePoints()
                    ghost.startSpawn()
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -=  1

    def checkFruitEvents(self):
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.score += self.fruit.points
    
    def listSuccessorGamestates(self):
        stop = self.update(STOP)
        up = self.update(UP)
        down = self.update(DOWN)
        left = self.update(LEFT)
        right = self.update(RIGHT)
        portal = self.update(PORTAL)
        return [stop, up, down, left, right, portal]

    def update(self, direction):
        copy = GameState(self.clock, self.pacman, self.fruit, self.level, self.lives, self.score, self.nodes, self.pellets, self.ghosts, self.mazedata, self.fruitCaptured)
        dt = copy.clock.tick(30) / 1000.0 
        copy.pacman.update(dt, direction)
        copy.ghosts.update(dt)      
        if copy.fruit is not None:
            copy.fruit.update(dt)
        copy.checkPelletEvents()
        copy.checkGhostEvents()
        copy.checkFruitEvents()
        return GameState(copy.clock, copy.pacman, copy.fruit, copy.level, copy.lives, copy.score, copy.nodes, copy.pellets, copy.ghosts, copy.mazedata, copy.fruitCaptured)

def aiEngine(clock, pacman, fruit, level, lives, score, nodes, pellets, ghosts, mazedata, fruitCaptured):
    current = GameState(clock, pacman, fruit, level, lives, score, nodes, pellets, ghosts, mazedata, fruitCaptured)
    _, next = minimax(current, 0, True, -inf, inf)
    return next.pacman.direction

def heuristic(gamestate):
    if gamestate is not None:
        return randint(-100,100)
    return 0

def minimax(gamestate, depth, isMaximizingPlayer, alpha, beta):
    if depth == MAX_DEPTH:
        return heuristic(gamestate), gamestate
    if isMaximizingPlayer:
        bestVal = -inf
        bestMove = None
        successors = gamestate.listSuccessorGamestates()
        for successorGamestate in successors:
            value, move = minimax(successorGamestate, depth+1, False, alpha, beta)
            if value > bestVal:
                bestVal, bestMove = value, move
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestMove
    else:
        bestVal = inf
        bestMove = None
        successors = gamestate.listSuccessorGamestates()
        for successorGamestate in successors:
            value, move = minimax(successorGamestate, depth+1, True, alpha, beta)
            if value < bestVal:
                bestVal, bestMove = value, move
            beta = min(beta, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestMove