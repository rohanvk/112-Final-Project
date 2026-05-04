import random
import time
from board import Cell

from solver import isBoardSolvableNoGuesses, getNextSolverAction
from solver_utils import analyze_tier_1, analyze_tier_2, analyze_global
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
    app._solverQueue = []
    app._solverCircleX = None
    app._solverCircleY = None
    app._solverTargetX = None
    app._solverTargetY = None

    # Stop all playing sounds safely (used ai here)
    for attr in ['loseMusic', 'winHarp', 'winMusic']:
        try:
            sound = getattr(app, attr, None)
            if sound is not None:
                sound.pause()
        except:
            pass

def _buildSafeZone(startRow, startCol, rows, cols):
    safeZones = []
    if rows > 20 or cols > 20:
        # 5x5 safe area for large boards
        r = min(max(startRow, 2), rows - 3)
        c = min(max(startCol, 2), cols - 3)
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                safeZones.append((r + dr, c + dc))
    elif rows > 8 or cols > 10:
        # 3x3 safe area for medium boards
        r = min(max(startRow, 1), rows - 2)
        c = min(max(startCol, 1), cols - 2)
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                safeZones.append((r + dr, c + dc))
    elif rows >= 8 and cols >= 10:
        # 3x2 safe area for easy-sized boards (3 cols x 2 rows)
        r = min(startRow, rows - 2)
        c = min(max(startCol, 1), cols - 2)
        for dr in range(0, 2):
            for dc in range(-1, 2):
                safeZones.append((r + dr, c + dc))
    else:
        # 2x2 safe area for small boards
        r = min(startRow, rows - 2)
        c = min(startCol, cols - 2)
        for dr in range(0, 2):
            for dc in range(0, 2):
                safeZones.append((r + dr, c + dc))
    return safeZones

def getSafeZoneSize(rows, cols):
    return len(_buildSafeZone(rows // 2, cols // 2, rows, cols))

def placeMines(app, startRow, startCol):
    safeZones = _buildSafeZone(startRow, startCol, app.rows, app.cols)

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
            
    return safeZones

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
        safeZones = placeMines(app, 0, 0)
        app.firstClick = False
        for r, c in safeZones:
            revealCell(app, r, c)
    
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
        try:
            if app.bigDigSound is not None and not getattr(app, 'muted', False):
                app.bigDigSound.play(restart=True)
        except:
            pass

    #otherwise pick a sound based on the number of mines adjacent
    elif revealedCount > 0:
        adj = cell.adjacentMines
        try:
            if 1 <= adj <= len(app.digSounds):
                if app.digSounds[adj-1] is not None and not getattr(app, 'muted', False):
                    app.digSounds[adj-1].play(restart=True)
            elif len(app.digSounds) > 0:
                if app.digSounds[0] is not None and not getattr(app, 'muted', False):
                    app.digSounds[0].play(restart=True)
        except:
            pass

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

            # First, execute the pending action (circle has arrived by now)
            pending = getattr(app, '_pendingSolverAction', None)
            if pending:
                _performSolverAction(app, pending)
                app._pendingSolverAction = None
            
            # Then, get the next action and set it as pending (circle will travel there)
            nextAction = None
            if getattr(app, '_solverQueue', []):
                nextAction = app._solverQueue.pop(0)
            else:
                nextAction = getNextSolverAction(app)
                if nextAction is None:
                    # Try full solver before giving up
                    _fillSolverQueue(app)
                    if getattr(app, '_solverQueue', []):
                        nextAction = app._solverQueue.pop(0)
            
            if nextAction:
                _setSolverTarget(app, nextAction)
                app._pendingSolverAction = nextAction
            elif not pending:
                # No pending was executed and no next found — truly done
                app.solverTarget = None
                app.autoSolve = False
        else:
            app.autoSolveTimer -= 1

def _setSolverTarget(app, action):
    actType, (r, c) = action
    app.solverTarget = (r, c)
    
    # Set target pixel position for the animated circle
    cellW = app.boardWidth / app.cols
    cellH = app.boardHeight / app.rows
    targetX = app.boardLeft + c * cellW + cellW / 2
    targetY = app.boardTop + r * cellH + cellH / 2
    app._solverTargetX = targetX
    app._solverTargetY = targetY
    # Snap to target if circle hasn't been placed yet
    if getattr(app, '_solverCircleX', None) is None:
        app._solverCircleX = targetX
        app._solverCircleY = targetY

def _performSolverAction(app, action):
    actType, (r, c) = action
    
    cell = app.board[r][c]
    if actType == 'reveal':
        if app.firstClick:
            safeZones = placeMines(app, r, c)
            app.firstClick = False
            app.startTime = time.time() - 1
            app.timer = 1
            for sr, sc in safeZones:
                revealCell(app, sr, sc)
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

def _fillSolverQueue(app):
    #Run the full solver (same logic as the hidden solver) to collect all remaining actions
    rows, cols = app.rows, app.cols
    board = app.board
    revealed = set((r, c) for r in range(rows) for c in range(cols) if board[r][c].revealed)
    known_mines = set((r, c) for r in range(rows) for c in range(cols) if board[r][c].flagged)
    
    queue = []
    
    #Simulate the hidden solver, collecting actions in order
    while True:
        progress = False
        
        actions = analyze_tier_1(board, rows, cols, revealed, known_mines)
        if actions:
            for actType, cell in actions:
                if actType == 'reveal' and cell not in revealed:
                    queue.append(('reveal', cell))
                    revealed.add(cell)
                    # Simulate flood-fill for zero cells
                    if board[cell[0]][cell[1]].adjacentMines == 0:
                        flood = [cell]
                        while flood:
                            fr, fc = flood.pop()
                            for dr in [-1, 0, 1]:
                                for dc in [-1, 0, 1]:
                                    nr, nc = fr + dr, fc + dc
                                    if 0 <= nr < rows and 0 <= nc < cols:
                                        if (nr, nc) not in revealed and (nr, nc) not in known_mines:
                                            revealed.add((nr, nc))
                                            if board[nr][nc].adjacentMines == 0:
                                                flood.append((nr, nc))
                elif actType == 'flag' and cell not in known_mines:
                    queue.append(('flag', cell))
                    known_mines.add(cell)
            progress = True
        
        if not progress:
            actions = analyze_tier_2(board, rows, cols, revealed, known_mines)
            if actions:
                for actType, cell in actions:
                    if actType == 'reveal' and cell not in revealed:
                        queue.append(('reveal', cell))
                        revealed.add(cell)
                        if board[cell[0]][cell[1]].adjacentMines == 0:
                            flood = [cell]
                            while flood:
                                fr, fc = flood.pop()
                                for dr in [-1, 0, 1]:
                                    for dc in [-1, 0, 1]:
                                        nr, nc = fr + dr, fc + dc
                                        if 0 <= nr < rows and 0 <= nc < cols:
                                            if (nr, nc) not in revealed and (nr, nc) not in known_mines:
                                                revealed.add((nr, nc))
                                                if board[nr][nc].adjacentMines == 0:
                                                    flood.append((nr, nc))
                    elif actType == 'flag' and cell not in known_mines:
                        queue.append(('flag', cell))
                        known_mines.add(cell)
                progress = True
        
        if not progress:
            actions = analyze_global(rows, cols, app.numMines, revealed, known_mines)
            if actions:
                for actType, cell in actions:
                    if actType == 'reveal' and cell not in revealed:
                        queue.append(('reveal', cell))
                        revealed.add(cell)
                    elif actType == 'flag' and cell not in known_mines:
                        queue.append(('flag', cell))
                        known_mines.add(cell)
                progress = True
        
        if not progress:
            break
    
    app._solverQueue = queue
