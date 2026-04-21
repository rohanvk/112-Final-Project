from cmu_graphics import *
import random

class Cell:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.hasMine = False
        self.revealed = False
        self.flagged = False
        self.adjacentMines = 0
        self.isAnimating = False #animation data
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
        self.waveDelay = 0

def placeMines(app, startRow, startCol):
    #Safe zone (the clicked cell and its 8 neighbors) some ai used here for planning
    safeZones = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            safeZones.append((startRow + dr, startCol + dc))

    # Place mines using random.sample
    candidates = []
    for row in range(app.rows):
        for col in range(app.cols):
            if (row, col) not in safeZones:
                candidates.append((row, col))

    # Make sure we don't try to place more mines than available cells
    numMines = min(app.numMines, len(candidates))
    minePositions = random.sample(candidates, numMines)
    for (row, col) in minePositions:
        app.board[row][col].hasMine = True
    
    #Count neighbors, some ai used here for boundary check
    for row in range(app.rows):
        for col in range(app.cols):
            if not app.board[row][col].hasMine:
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        newRow, newCol = row + dr, col + dc
                        if (0 <= newRow < app.rows and 0 <= newCol < app.cols and 
                            app.board[newRow][newCol].hasMine):
                            count += 1
                app.board[row][col].adjacentMines = count
        
def getCell(app, x, y):
    if (app.boardLeft <= x < app.boardLeft + app.boardWidth and
        app.boardTop <= y < app.boardTop + app.boardHeight):
        col = int((x - app.boardLeft) / (app.boardWidth / app.cols))
        row = int((y - app.boardTop) / (app.boardHeight / app.rows))
        return (row, col)
    return None


def revealAllMines(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col].hasMine:
                app.board[row][col].revealed = True

def checkWin(app):
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            if not cell.hasMine and not cell.revealed:
                return False
    return True

def revealCell(app, r, c): # recursive reveal
    if not (0 <= r < app.rows and 0 <= c < app.cols): return
    cell = app.board[r][c]
    if cell.revealed: return

    cell.revealed = True
    cell.isAnimating = True
    cell.animScale = 1.0
    cell.animOffsetX = 0
    cell.animOffsetY = 0
    cell.animDx = random.choice([-1, 1]) * random.randint(3, 8)
    cell.animDy = random.choice([-1, 1]) * random.randint(3, 8)

    if cell.adjacentMines == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                revealCell(app, r + dr, c + dc)

def drawRoundedRect(x, y, w, h, radius, fill='black', border=None, borderWidth=1):
    # Used AI to make this function, draws 4 circles and two rectangles
    drawRect(x + radius, y, w - 2 * radius, h, fill=fill)
    drawRect(x, y + radius, w, h - 2 * radius, fill=fill)
    
    drawCircle(x + radius, y + radius, radius, fill=fill)
    drawCircle(x + w - radius, y + radius, radius, fill=fill)
    drawCircle(x + radius, y + h - radius, radius, fill=fill)
    drawCircle(x + w - radius, y + h - radius, radius, fill=fill)
    
    # Outlines rectangles
    if border != None:
        # Edges
        drawLine(x + radius, y, x + w - radius, y, fill=border, lineWidth=borderWidth) # Top
        drawLine(x + radius, y + h, x + w - radius, y + h, fill=border, lineWidth=borderWidth) # Bottom
        drawLine(x, y + radius, x, y + h - radius, fill=border, lineWidth=borderWidth) # Left
        drawLine(x + w, y + radius, x + w, y + h - radius, fill=border, lineWidth=borderWidth) # Right
        
        # Arcs
        d = radius * 2
        drawArc(x + w - radius, y + radius, d, d, 0, 90, fill=None, border=border, borderWidth=borderWidth) # Top-Right
        drawArc(x + radius, y + radius, d, d, 90, 90, fill=None, border=border, borderWidth=borderWidth) # Top-Left
        drawArc(x + radius, y + h - radius, d, d, 180, 90, fill=None, border=border, borderWidth=borderWidth) # Bottom-Left
        drawArc(x + w - radius, y + h - radius, d, d, 270, 90, fill=None, border=border, borderWidth=borderWidth) # Bottom-Right