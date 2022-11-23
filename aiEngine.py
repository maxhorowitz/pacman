from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from constants import *
from pacman import Pacman

from random import randint
from math import inf

MAX_DEPTH = 2

class GameState(object):
    def __init__(self, clock, pacman, fruit, level, lives, score, nodes, pellets, ghosts, mazedata, fruitCaptured):
        self._id = randint(1000000000, 9999999999)
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
        # moves = [STOP, UP, DOWN, LEFT, RIGHT, PORTAL]
        moves = [STOP, UP, DOWN, LEFT, RIGHT]
        successors = []
        successor = None
        for move in moves:
            # if move == PORTAL:
            #     if self.pacman.overshotTarget():
            #         self.pacman.node = self.pacman.target
            #         if self.pacman.node.neighbors[PORTAL] is not None:
            #             self.pacman.node = self.pacman.node.neighbors[PORTAL]
            #         # self.pacman.target = self.pacman.getNewTarget(direction)
            #         # if self.pacman.target is not self.pacman.node:
            #         #     self.pacman.direction = direction
            #         # else:
            #         #     self.pacman.target = self.pacman.getNewTarget(self.pacman.direction)
            #         # if self.pacman.target is self.pacman.node:
            #         #     self.pacman.direction = STOP
            #         self.pacman.setPosition()
            # else:
            successor = self.update(move)
            successors.append(successor)
        return successors

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
    h, next = minimax(current, 0, True, -inf, inf)
    print("Selected gamestate._id", str(next._id), "with value", str(h))
    return next.pacman.direction

def heuristic(gamestate):
    return gamestate.lives*gamestate.score

def minimax(gamestate, depth, isMaximizingPlayer, alpha, beta):
    if depth == MAX_DEPTH:
        return heuristic(gamestate), gamestate
    if isMaximizingPlayer:
        bestVal = -inf
        bestSuccessor = None
        successors = gamestate.listSuccessorGamestates()
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
        successors = gamestate.listSuccessorGamestates()
        for successorGamestate in successors:
            value, successor = minimax(successorGamestate, depth+1, True, alpha, beta)
            if value < bestVal:
                bestVal, bestSuccessor = value, successor
            beta = min(beta, bestVal)
            if beta <= alpha:
                break
        return bestVal, bestSuccessor