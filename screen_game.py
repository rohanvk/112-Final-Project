from cmu_graphics import *
import time
from game_engine import restartApp, placeMines, getCell, checkWin, startGameOver, triggerWin, wonGame, autoSolverLogic, shakeScreen, lossAnimation
from ui import drawCells, drawTimer, drawStatus, drawMenu, drawGameScreens
from animations import stepCellAnimations, stepFlagAnimations, stepFlagDespawn, stepConfetti, drawConfetti, removeFlag
from ui_checks import switchScreen, _isGuarded, checkMenuHover, checkAudioButton, checkBackButton, autoSolver, menuLogic, startOverButton

#Handles the game screen

def game_onMouseMove(app, mouseX, mouseY):
    if app.gameOver:
        app.hoveredCell = None
        return
        
    coords = getCell(app, mouseX, mouseY)
    
    if app.hoveredCell != coords:
        app.hoveredCell = coords

    #used some ai to get the hover for the menu
    checkMenuHover(app, mouseX, mouseY)

#ai helped build up some of the CMU Graphics screens and debug
def game_onMousePress(app, mouseX, mouseY, button=0):
    if _isGuarded(app): return
    if checkAudioButton(app, mouseX, mouseY): return
    
    backResult = checkBackButton(app, mouseX, mouseY)
    if backResult == 'start':
        switchScreen(app, 'start')
        return
    elif backResult:
        return

    # auto solve button
    if autoSolver(app,mouseX,mouseY): return

    # menus and restart button
    menuResult = menuLogic(app,mouseX,mouseY)
    if menuResult == 'custom':
        switchScreen(app, 'custom')
        return
    elif menuResult:
        return
    if startOverButton(app,mouseX,mouseY):
        app.autoSolve = False # Reset on new game
        return

    if getattr(app, 'autoSolve', False): return # Block manual play when auto solving

    coords = getCell(app, mouseX, mouseY)
    if coords is None: return
    row, col = coords
    cell = app.board[row][col]

    # Right click (flag)
    if button == 2:
        if not cell.revealed:
            if cell.flagged: # remove flag
                removeFlag(cell)
                #ai helped with all of the audio management as it had significant bugs
                try:
                    if getattr(app, 'unplantSound', None) and not getattr(app, 'muted', False): app.unplantSound.play(restart=True)
                except:
                    pass

            cell.flagged = not cell.flagged

            if cell.flagged: #add flag
                cell.isFlagAnimating = True
                cell.flagScale = 0.1
                try:
                    if getattr(app, 'plantSound', None) and not getattr(app, 'muted', False): app.plantSound.play(restart=True)
                except:
                    pass

    # Left click (open)
    elif button == 0:
        if cell.flagged: return 
        
        if app.firstClick:
            placeMines(app, row, col)
            app.firstClick = False
            app.startTime = time.time() - 1
            app.timer = 1

        if cell.hasMine:
            startGameOver(app, cell, coords)
        else:
            wonGame(app, coords)

def game_onKeyPress(app, key):
    if key == 'space':
        restartApp(app)
        return
        
    if not app.gameOver:
        if key == 'p': 
            app.paused = not app.paused
        if key == 'e':
            startGameOver(app)
        if key == 'w':
            triggerWin(app)

def game_onStep(app):
    if not getattr(app, 'isLoaded', False): return
    app.screenGuard = False
    app.soundsPlayedThisStep = 0

    #dont draw if screen is too small
    if app.boardWidth != app.width or app.boardHeight != max(1, app.height - 90):
        app.boardWidth = app.width
        app.boardHeight = max(1, app.height - 90)

    shakeScreen(app)
    if not app.paused and not app.gameOver:
        takeStep(app)
        
        autoSolverLogic(app)

    if app.gameOver and getattr(app, 'autoSolve', False):
        app.autoSolve = False
        app.solverTarget = None
    
    #animations!
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            stepCellAnimations(cell)
            stepFlagAnimations(cell)
            stepFlagDespawn(cell)
    if app.gameOver:
        if not app.isWin:
            # lose = mines explode
            lossAnimation(app)
        else:
            if app.winFlashTimer > 0:
                app.winFlashTimer -= 1
            
            # win music 
            if app.winnerMusicTimer > 0:
                app.winnerMusicTimer -= 1
                if app.winnerMusicTimer == 0:
                    try:
                        if getattr(app, 'winMusic', None) and not getattr(app, 'muted', False): app.winMusic.play(restart=True)
                    except:
                        pass

        stepConfetti(app)

def takeStep(app):
    app.timer = int(time.time() - app.startTime)

def game_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(74, 117, 44)) # Background
    if app.boardHeight > 0:
        drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, fill='lightGray') # Board background
        drawCells(app)

    drawTimer(app)
    drawStatus(app)
    drawMenu(app)
    drawConfetti(app)
    drawGameScreens(app)
