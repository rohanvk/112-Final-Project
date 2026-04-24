from cmu_graphics import *

#When a cell is animating, it recieves all of this data
class AnimationData:
    def __init__(self):
        #animation data
        self.isAnimating = False 
        self.animScale = 1.0     
        self.animDx = 0         
        self.animDy = 0         
        self.animOffsetX = 0   
        self.animOffsetY = 0
        self.flagScale = 0.0
        self.isFlagAnimating = False
        self.isFlagDespawning = False
        self.flagDespawnScale = 1.0
        self.flagDespawnOffsetX = 0
        self.flagDespawnOffsetY = 0
        self.flagDespawnDx = 0
        self.flagDespawnDy = 0
        self.waveDelay = -1

#Cell class inherits from animationdata because we only need certain attributes for all cells
class Cell(AnimationData):
    def __init__(self, row, col):
        super().__init__()
        self.row, self.col = row, col
        self.hasMine = False
        self.revealed = False
        self.flagged = False
        self.adjacentMines = 0
