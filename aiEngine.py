from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from constants import *
from pacman import Pacman
# from entity import Entity

def aiEngine(clock, fruit, level, lives, score, nodes, pellets, ghosts):
    
    for i in range(0, 5):
        print(lives)

    return RIGHT

class GameState(object):
    def __init__(self, clock, pacman, fruit, level, lives, score, nodes, pellets, ghosts):
        self.clock = clock
        self.pacman = pacman
        self.fruit = fruit
        self.level = level
        self.lives = lives
        self.score = score
        self.nodes = nodes
        self.pellets = pellets
        self.ghosts = ghosts
    
    def listSuccessorGameState(self):
        # STOP (0)
        # UP (1)
        # DOWN (-1)
        # LEFT (2)
        # RIGHT (-2)
        # PORTAL (3)
        return NotImplemented