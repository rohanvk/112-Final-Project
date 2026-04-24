import random
import time
from board import Cell

from solver import isBoardSolvableNoGuesses, getNextSolverAction
from animations import popFlags, spawnWinConfetti, openMines

#This file runs the game play loop

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

    #automatically stops autosolver
    app.autoSolve = False
    app.solverTarget = None

    # Stop all playing sounds safely (used ai here)
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
        #this makes the larger boards faster to solve with the algorithm
    safeRange = 2 if (app.rows > 20 or app.cols > 20) else 1
    safeZones = []
    for dr in range(-safeRange, safeRange + 1):
        for dc in range(-safeRange, safeRange + 1):
            safeZones.append((startRow + dr, startCol + dc))

    # Precompute candidates for mines
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
        
        # Only add numbers when on mines
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

#function from tetris/snake
def getCell(app, x, y):
    if (app.boardLeft <= x < app.boardLeft + app.boardWidth and
        app.boardTop <= y < app.boardTop + app.boardHeight):
        col = int((x - app.boardLeft) / (app.boardWidth / app.cols))
        row = int((y - app.boardTop) / (app.boardHeight / app.rows))
        return (row, col)
    return None

#open all cells with mines up
def revealAllMines(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col].hasMine:
                app.board[row][col].revealed = True

#check if all without mines revealed
def checkWin(app):
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            if not cell.hasMine and not cell.revealed:
                return False
    return True

#reveal all adjacent empty cells
def revealCell(app, r, c): 
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
    # recursive reveal
    if cell.adjacentMines == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                count += revealCell(app, r + dr, c + dc)
    return count

#sets up gameover
def startGameOver(app, cell=None, coords=None):
    #first click is mine free
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
    
    #open cell if no e command used
    if cell is not None:
        cell.revealed = True
    
    #optional coords bc pressing e (dev command) starts gameover without coords
    row = coords[0] if coords else 0
    col = coords[1] if coords else 0

    #add wavedelay factor based on distance from clicked cell (coords)
    for r in range(app.rows):
        for c in range(app.cols):
            checkCell = app.board[r][c]
            #intial cell explodes
            if r-row == 0 and c - col == 0 and coords is not None:
                checkCell.waveDelay = 1
                
            #all other cells with mines get a delay
            elif (((checkCell.hasMine or checkCell.flagged) and not checkCell.revealed) 
            or (coords is None and (checkCell.hasMine or checkCell.flagged))):
                dist = ((r - row)**2 + (c - col)**2)**0.5
                checkCell.waveDelay = int(dist * 12)

#visible screen shake on big reveal and explosions
def shakeScreen(app):
    if getattr(app, 'shakeTimer', 0) > 0:
        app.shakeTimer -= 1
        app.boardLeft = random.randint(-3, 3)
        app.boardTop = 90 + random.randint(-3, 3)
    else:
        app.boardLeft = 0
        app.boardTop = 90

def lossAnimation(app):
    stillExploding = False
    #go through the cells and explode the next
    for r in range(app.rows):
        for c in range(app.cols):
            cell = app.board[r][c]
            if (cell.hasMine or cell.flagged) and cell.waveDelay > -1:
                stillExploding = True
                cell.waveDelay -= 1
                if cell.waveDelay <= 0:
                    if cell.flagged:
                        popFlags(cell)
                    if cell.hasMine:
                        openMines(app, cell, r, c)
    
    #play the music and show the end screen when done
    if not stillExploding:
        if not app.endflag:
            try:
                if getattr(app, 'loseMusic', None) and not getattr(app, 'muted', False): app.loseMusic.play(restart=True)
            except:
                pass
        app.endflag = True

def triggerWin(app):
    #on the first click place the mines
    if app.firstClick:
        placeMines(app, 0, 0)
        app.firstClick = False
    
    #show win screen and flash
    app.gameOver = True
    app.isWin = True
    app.endflag = True
    app.forcedWin = True
    app.winFlashTimer = 10
    
    # Win audio
    try:
        if getattr(app, 'loseMusic', None): app.loseMusic.pause()
        if getattr(app, 'winMusic', None): app.winMusic.pause()
    except:
        pass

    try:
        if getattr(app, 'winHarp', None) and not getattr(app, 'muted', False): app.winHarp.play()
    except:
        pass
    app.winnerMusicTimer = 80 # Play win music after harp (hard coded because cmu audio was quite buggy with loops)

    # Save score
    if app.currentDifficulty in app.bestScores:
        app.bestScores[app.currentDifficulty].append(app.timer)
        app.bestScores[app.currentDifficulty].sort()

    # Pop all flags and generate confetti
    app.confetti = []
    for r in range(app.rows):
        for c in range(app.cols):
            checkCell = app.board[r][c]
            if checkCell.flagged:
                popFlags(checkCell)
    spawnWinConfetti(app)

def wonGame(app, coords):
    row, col = coords
    cell = app.board[row][col]
    revealedCount = revealCell(app, row, col)
    
    #if its a big reveal special sound
    if revealedCount > 10:
        if app.bigDigSound is not None and not getattr(app, 'muted', False):
            app.bigDigSound.play(restart=True)

    #otherwise pick a sound based on the number of mines adjacent
    elif revealedCount > 0:
        adj = cell.adjacentMines
        if 1 <= adj <= 8:
            if app.digSounds[adj-1] is not None and not getattr(app, 'muted', False):
                app.digSounds[adj-1].play(restart=True)
        else:
            if app.digSounds[0] is not None and not getattr(app, 'muted', False):
                app.digSounds[0].play(restart=True)

    if revealedCount > 10:
        app.shakeTimer = 5 # shake screen
    
    #check if we won
    if checkWin(app) or app.forcedWin:
        triggerWin(app)

#Used some ai to make this, overall outline was mine
#This breaks the solver logic into steps for viewing on the board
def autoSolverLogic(app):
    if getattr(app, 'autoSolve', False):
        if getattr(app, 'autoSolveTimer', 0) <= 0:
            app.autoSolveTimer = 2 
            # run every 2 steps

            action = getNextSolverAction(app)
            #Perform either a reveal or flag on the cell
            if action:
                actType, (r, c) = action
                app.solverTarget = (r, c)
                
                #Handle first clicks, wins, and game overs (unlikely)
                cell = app.board[r][c]
                if actType == 'reveal':
                    if app.firstClick:
                        placeMines(app, r, c)
                        app.firstClick = False
                        app.startTime = time.time() - 1
                        app.timer = 1
                    if not cell.flagged:
                        if cell.hasMine:
                            startGameOver(app, cell, (r, c))
                        else:
                            wonGame(app, (r, c))
                elif actType == 'flag':
                    if not cell.flagged:
                        cell.flagged = True
                        cell.isFlagAnimating = True
                        cell.flagScale = 0.1
                        try:
                            if getattr(app, 'plantSound', None) and not getattr(app, 'muted', False): app.plantSound.play(restart=True)
                        except:
                            pass
            #if we dont't have a target pause and wait for the user to make a guess or we are finished
            else:
                app.solverTarget = None
                app.autoSolve = False # Stuck or done
        else:
            app.autoSolveTimer -= 1
