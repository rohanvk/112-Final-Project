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
    app.endflag = False
    app.winnerMusicTimer = 0
    app.autoSolve = False
    app.solverTarget = None

    # Stop all playing sounds safely
    for attr in ['loseMusic', 'winHarp', 'winMusic']:
        try:
            sound = getattr(app, attr, None)
            if sound is not None:
                sound.pause()
        except:
            pass


def placeMines(app, startRow, startCol):
    # Set safe zone size based on board dimensions (some ai used here)
    # Boards larger than 20x20 get a 5x5 safe area, smaller get 3x3
    safeRange = 2 if (app.rows > 20 or app.cols > 20) else 1
    safeZones = []
    for dr in range(-safeRange, safeRange + 1):
        for dc in range(-safeRange, safeRange + 1):
            safeZones.append((startRow + dr, startCol + dc))

    from solver import isBoardSolvableNoGuesses
    
    # Precompute candidates
    candidates = []
    safeZonesSet = set(safeZones)
    for row in range(app.rows):
        for col in range(app.cols):
            if (row, col) not in safeZonesSet:
                candidates.append((row, col))
    
    numMines = min(app.numMines, len(candidates))

    while True:
        # Reset board
        for row in range(app.rows):
            for col in range(app.cols):
                app.board[row][col].hasMine = False
                app.board[row][col].adjacentMines = 0
                
        # Place mines
        minePositions = random.sample(candidates, numMines)
        for (row, col) in minePositions:
            app.board[row][col].hasMine = True
        
        # Only add on mines
        for (r, c) in minePositions:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr == 0 and dc == 0: continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < app.rows and 0 <= nc < app.cols:
                        app.board[nr][nc].adjacentMines += 1
                    
        # No guessing!
        if getattr(app, 'noGuessMode', True):
            if isBoardSolvableNoGuesses(app, startRow, startCol):
                break
        else:
            break
        
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

def startGameOver(app, cell=None, coords=None):
    if app.firstClick:
        placeMines(app, 0, 0)
        app.firstClick = False

    app.gameOver = True
    app.isWin = False
    app.shakeTimer = 8
    
    # Stop win music if it's playing
    try:
        if getattr(app, 'winHarp', None): app.winHarp.pause()
        if getattr(app, 'winMusic', None): app.winMusic.pause()
    except:
        pass

    if cell is not None:
        cell.revealed = True
        
    row = coords[0] if coords else 0
    col = coords[1] if coords else 0

    for r in range(app.rows):
        for c in range(app.cols):
            checkCell = app.board[r][c]
            if r-row == 0 and c - col == 0 and coords is not None:
                checkCell.waveDelay = 1
            elif (((checkCell.hasMine or checkCell.flagged) and not checkCell.revealed) 
            or (coords is None and (checkCell.hasMine or checkCell.flagged))):
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