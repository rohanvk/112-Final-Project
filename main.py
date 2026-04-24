#For all citations of AI, Gemini Pro 3.1 was used (Claude Opus 4.6 (thinking and planning) was used for finding bugs)
#All images and audio from the Google Minesweeper game unless otherwise cited
#Dev commands: p to pause, w to win, e to lose

from cmu_graphics import *
from PIL import Image as PILImage #image optimization
import time #need because otherwise timer tracks framerate
from board import *
from ui import *
from solver import *
from animations import *

def onAppStart(app):
    app.isLoaded = False
    app.width = app.height = 750
    app.stepsPerSecond = 20
    app.rows = 14
    app.cols = 18
    app.boardLeft = 0
    app.boardTop = 90
    app.boardWidth = app.width
    app.boardHeight = app.height - 90
    app.cellBorderWidth = 0.5
    app.paused = False
    app.board = [[Cell(row, col) for col in range (app.cols)] for row in range(app.rows)]

    app.score = 0
    app.gameOver = False
    app.isWin = False
    app.forcedWin = False
    app.numMines = 40
    app.firstClick = True
    app.startTime = time.time()
    app.timer = 0
    app.hoveredCell = None

    app.confetti = []
    app.bestScores = {"Easy": [], "Medium": [], "Hard": []}
    app.winFlashTimer = 0
    app.isDropdownOpen = False
    app.menuHoveredItem = None
    app.currentDifficulty = "Medium"
    app.menuShiftX = 0       
    app.noGuessMode = True
    app.checkmarkIndentX = 30
    app.endflag = False
    app.winnerMusicTimer = 0

    # Audio
    app.bigDigSound = Sound('audio/game_audio BIG_DIG.mp3')
    app.mineSounds = [s for s in [Sound(f'audio/game_audio MINE_{i}.mp3') for i in range(1, 6)] if s is not None]
    app.digSounds = [s for s in [Sound(f'audio/game_audio DIG_REVEAL_{i}.mp3') for i in range(1, 9)] if s is not None]
    app.soundsPlayedThisStep = 0
    app.plantSound = Sound('audio/game_audio PLANT_FLAG.mp3')
    app.unplantSound = Sound('audio/game_audio UNPLANT_FLAG.mp3')
    app.loseMusic = Sound('audio/music_audio LOSE_MUSIC.mp3')
    app.winHarp = Sound('audio/music_audio WIN_WATER_HARP.mp3')
    app.winMusic = Sound('audio/music_audio WINNER_MUSIC.mp3')

    app.difficulties = {
        "Easy": (8, 10, 10),
        "Medium": (14, 18, 40),
        "Hard": (20, 24, 99)
    }
    
    # Menu location and size
    app.menuX = 20
    app.menuY = 25
    app.menuW = 100
    app.menuH = 40

    app.numberColors = {
        1: (rgb(72, 133, 237), rgb(47, 86, 154)),   # Blue
        2: (rgb(0, 135, 68), rgb(0, 88, 44)),       # Green
        3: (rgb(219, 50, 54), rgb(142, 33, 35)),    # Red
        4: (rgb(182, 72, 242), rgb(118, 47, 157)),  # Purple
        5: (rgb(244, 132, 13), rgb(159, 86, 8)),    # Orange
        6: (rgb(72, 230, 241), rgb(47, 150, 157)),  # Cyan
        7: (rgb(237, 68, 181), rgb(154, 44, 118)),  # Pink
        8: (rgb(244, 194, 13), rgb(159, 126, 8))    # Yellow
    }
    app.textColors = {
        1: rgb(25, 118, 210),   # Blue
        2: rgb(56, 142, 60),    # Green
        3: rgb(211, 47, 47),    # Red
        4: rgb(123, 31, 162),   # Purple
        5: rgb(255, 143, 0),    # Orange
        6: rgb(0, 152, 165),    # Teal
        7: rgb(66, 66, 66),     # Dark Gray
        8: rgb(160, 159, 158)   # Light Gray
    }

    #image optimization (ai helped with this)
    imageWidth = 60
    imageHeight = 60
        
    rawFlag = PILImage.open('images/flag.png')
    resizedFlag = rawFlag.resize((imageWidth, imageHeight))
    app.flagImage = CMUImage(resizedFlag)
    rawArrow = PILImage.open('images/downArrow.png')
    app.downArrow = CMUImage(rawArrow)
    rawCheck = PILImage.open('images/checkmark.png')
    app.checkmark = CMUImage(rawCheck)
    rawTimer = PILImage.open('images/timerimage.png')
    resizedTimer = rawTimer.resize((44, 54))
    app.timerimage = CMUImage(resizedTimer)
    rawTry = PILImage.open('images/Try again.png')
    app.tryagain = CMUImage(rawTry)
    rawWin = PILImage.open('images/Win screen.png')
    app.winimage = CMUImage(rawWin)
    rawLose = PILImage.open('images/Lose screen.png')
    app.loseimage = CMUImage(rawLose)
    app.isLoaded = True


def onMouseMove(app, mouseX, mouseY):
    if app.gameOver:
        app.hoveredCell = None
        return
        
    coords = getCell(app, mouseX, mouseY)
    
    if app.hoveredCell != coords:
        app.hoveredCell = coords

    #used some ai to get the hover for the menu
    checkMenuHover(app, mouseX, mouseY)

def onMousePress(app, mouseX, mouseY, button=0):
    # Check Auto Solve button
    btnW, btnH = 90, 30
    btnX = app.width - btnW - 20
    btnY = 30
    if btnX <= mouseX <= btnX + btnW and btnY <= mouseY <= btnY + btnH:
        if button == 0 or button == 1:
            app.autoSolve = not getattr(app, 'autoSolve', False)
            app.solverTarget = None
            return

    # Allow menus and restart button even if auto-solving
    if menuLogic(app,mouseX,mouseY): return
    if startOverButton(app,mouseX,mouseY):
        app.autoSolve = False # Reset on new game
        return

    if getattr(app, 'autoSolve', False): return # Block manual play when auto solving

    coords = getCell(app, mouseX, mouseY)
    if coords is None: return
    row, col = coords
    cell = app.board[row][col]

    # Right Click (flag)
    if button == 2:
        if not cell.revealed:
            if cell.flagged: # remove flag
                removeFlag(cell)
                try:
                    if getattr(app, 'unplantSound', None): app.unplantSound.play(restart=True)
                except:
                    pass

            cell.flagged = not cell.flagged

            if cell.flagged: #add flag
                cell.isFlagAnimating = True
                cell.flagScale = 0.1
                try:
                    if getattr(app, 'plantSound', None): app.plantSound.play(restart=True)
                except:
                    pass

    # Left Click (open)
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

def onKeyPress(app, key):
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

def onStep(app):
    if not getattr(app, 'isLoaded', False): return
    app.soundsPlayedThisStep = 0

    if app.boardWidth != app.width or app.boardHeight != app.height - 90:
        app.boardWidth = app.width
        app.boardHeight = app.height - 90
    shakeScreen(app)
    if not app.paused and not app.gameOver:
        takeStep(app)
        
        # AUTO SOLVER LOGIC
        if getattr(app, 'autoSolve', False):
            if getattr(app, 'autoSolveTimer', 0) <= 0:
                app.autoSolveTimer = 2 # run every 2 ticks
                
                from solver import getNextSolverAction
                action = getNextSolverAction(app)
                if action:
                    actType, (r, c) = action
                    app.solverTarget = (r, c)
                    
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
                                if getattr(app, 'plantSound', None): app.plantSound.play(restart=True)
                            except:
                                pass
                else:
                    app.solverTarget = None
                    app.autoSolve = False # Stuck or done
            else:
                app.autoSolveTimer -= 1
                
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
                        if getattr(app, 'winMusic', None): app.winMusic.play(restart=True)
                    except:
                        pass

        stepConfetti(app)

def takeStep(app):
    app.timer = int(time.time() - app.startTime)

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(74, 117, 44)) # Background
    if app.boardHeight > 0:
        drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight, fill='lightGray') # Board background
        drawCells(app)

    drawTimer(app)
    drawStatus(app)
    drawMenu(app)
    drawConfetti(app)
    drawGameScreens(app)

def main():
    runApp()

main()