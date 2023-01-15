# Class for a piece. This just handles loading the model and setting initial
# position and color
from panda3d.core import LPoint3
BLACK = (0, 0, 0, 1)
WHITE = (1, 1, 1, 1)
HIGHLIGHT = (0, 1, 1, 1)
PIECEBLACK = (.2, .2, .2, 1)
BLACK_WALL = (.4, .4, .4, 1)
WHITE_WALL = (255,255,255,1)
class Piece(object):
    def __init__(self, square, color):
        self.obj = loader.loadModel(self.model)
        self.is_wall = 0
        self.is_pawn = 0
        if 'wall' in self.model:
            self.obj.setScale(0.1, 0.1, 0.1)
            self.obj.set_hpr(90, 0, 0)
            self.is_wall = 1
        elif 'pawn' in self.model:
            self.is_pawn = 1
            
        self.obj.reparentTo(render)
        if "WHITE" in color:
            self.obj.setColor(WHITE)
        elif "BLACK_WALL" in color:
            self.obj.setColor(BLACK_WALL)
        elif "BLACK" in color:
            self.obj.setColor(BLACK)
        self.square = square


# Classes for each type of chess piece
class Pawn(Piece):
    model = "models/pawn"

class Wall(Piece):
    model = "models/walls/wall2"

