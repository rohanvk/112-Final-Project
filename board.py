from cmu_graphics import *
import random
import time

class Cell:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.hasMine = False
        self.revealed = False
        self.flagged = False
        self.adjacentMines = 0
        
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

def restartApp(app):
    app.paused = False
    app.board = [[Cell(row, col) for col in range (app.cols)] for row in range(app.rows)]
    app.gameOver = False
    app.isWin = False
    app.firstClick = True
    app.timer = 0
    app.startTime = time.time()
    app.confetti = []
    app.hoveredCell = None
    app.winFlashTimer = 0
    app.shakeTimer = 0
    app.isDropdownOpen = False
    app.menuHoveredItem = None
    app.forcedWin = False


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
    if not (0 <= r < app.rows and 0 <= c < app.cols): return 0
    cell = app.board[r][c]
    if cell.revealed: return 0

    cell.revealed = True
    cell.isAnimating = True
    cell.animScale = 1.0
    cell.animOffsetX = 0
    cell.animOffsetY = 0
    cell.animDx = random.choice([-1, 1]) * random.randint(3, 8)
    cell.animDy = random.choice([-1, 1]) * random.randint(3, 8)

    count = 1
    if cell.adjacentMines == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                count += revealCell(app, r + dr, c + dc)
    return count

def startGameOver(app, cell, coords):
    app.gameOver = True
    app.isWin = False
    app.shakeTimer = 8
    cell.revealed = True
    row, col = coords

    for r in range(app.rows):
        for c in range(app.cols):
            checkCell = app.board[r][c]
            if r-row == 0 and c - col == 0:
                checkCell.waveDelay = 1
            elif (checkCell.hasMine or checkCell.flagged) and not checkCell.revealed:
                dist = ((r - row)**2 + (c - col)**2)**0.5
                checkCell.waveDelay = int(dist * 12)

def shakeScreen(app):
    if getattr(app, 'shakeTimer', 0) > 0:
        app.shakeTimer -= 1
        app.boardLeft = random.randint(-3, 3)
        app.boardTop = 90 + random.randint(-3, 3)
    else:
        app.boardLeft = 0
        app.boardTop = 90