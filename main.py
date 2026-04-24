#For all citations of AI, Gemini Pro 3.1 was used (Claude Opus 4.6 (thinking and planning) was used for finding bugs)
#All images and audio from the Google Minesweeper game unless otherwise cited
#Dev commands: p to pause, w to win, e to lose, space to reset game

from cmu_graphics import *
from PIL import Image as PILImage #image optimization
import time #need because otherwise timer tracks framerate
from board import *
from ui import *
from solver import *
from button import Button
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
    app.muted = False
    app.screenGuard = False
    app.customRows = 14
    app.customCols = 18
    app.customMines = 40
    app.customNoGuess = True
    app.customConfigured = False

    # Audio
    try:
        rawAudio = PILImage.open('images/Audio.png')
        resizedAudio = rawAudio.resize((30, 30))
        app.audioImage = CMUImage(resizedAudio)
    except:
        app.audioImage = None

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
        "Hard": (20, 24, 99),
        "Custom": (14, 18, 40)
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
    rawOpening = PILImage.open('images/Minesweeper opening page.png')
    app.openingImage = CMUImage(rawOpening)
    app.isLoaded = True


def game_onMouseMove(app, mouseX, mouseY):
    if app.gameOver:
        app.hoveredCell = None
        return
        
    coords = getCell(app, mouseX, mouseY)
    
    if app.hoveredCell != coords:
        app.hoveredCell = coords

    #used some ai to get the hover for the menu
    checkMenuHover(app, mouseX, mouseY)

def switchScreen(app, screenName):
    app.screenGuard = True
    setActiveScreen(screenName)

def _isGuarded(app):
    return getattr(app, 'screenGuard', False)

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

    # Right Click (flag)
    if button == 2:
        if not cell.revealed:
            if cell.flagged: # remove flag
                removeFlag(cell)
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

    if app.boardWidth != app.width or app.boardHeight != app.height - 90:
        app.boardWidth = app.width
        app.boardHeight = app.height - 90
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
    
def getStartButtons(app):
    cx = app.width / 2
    btnW, btnH = app.width * 0.27, app.height * 0.07
    gap = app.height * 0.08
    startY = app.height * 0.68
    return [
        Button(cx, startY + btnH/2, btnW, btnH, "Play", textSize=24),
        Button(cx, startY + gap + btnH/2, btnW, btnH, "Custom Mode", textSize=24),
        Button(cx, startY + gap*2 + btnH/2, btnW, btnH, "Instructions", textSize=24),
    ]

def start_redrawAll(app):
    skyColor = rgb(68, 191, 244)
    grassColor = rgb(74, 117, 44)
    splitY = app.height * 0.55
    drawRect(0, 0, app.width, splitY, fill=skyColor)
    drawRect(0, splitY, app.width, app.height - splitY, fill=grassColor)
    
    if getattr(app, 'openingImage', None):
        imgW = app.width * 0.8
        imgH = app.height * 0.25
        drawImage(app.openingImage, app.width/2, splitY, align='center',
                  width=imgW, height=imgH)
    
    drawLabel("MINESWEEPER", app.width/2, app.height * 0.15, size=60, bold=True, fill='white')
    
    for btn in getStartButtons(app):
        btn.draw()

def start_onMousePress(app, mouseX, mouseY):
    if _isGuarded(app): return
    buttons = getStartButtons(app)
    if buttons[0].contains(mouseX, mouseY):
        switchScreen(app, 'game')
    elif buttons[1].contains(mouseX, mouseY):
        switchScreen(app, 'custom')
    elif buttons[2].contains(mouseX, mouseY):
        switchScreen(app, 'instructions')

def start_onStep(app):
    app.screenGuard = False

def getInstructionsBackButton(app):
    btnW, btnH = 80, 40
    return Button(60, 40, btnW, btnH, "Back", textSize=16)

def instructions_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(74, 117, 44))
    drawLabel("Instructions", app.width/2, app.height * 0.1, size=40, bold=True, fill='white')
    rules = [
        "The Objective",
        "Clear the entire grid without detonating any hidden mines.",
        "You win when every single safe square has been revealed!",
        "",
        "The Controls",
        "Left-Click: Reveal a square. (If it's a mine, it's Game Over)",
        "Right-Click: Plant a flag. Use this to mark squares where you are sure a mine is hiding.",
        "Space: Press space to reset the game"
        "No Guess Mode: The game guarantees the board can be solved without guessing.",
        "",
        "The Numbers",
        "When you reveal an empty square, a number will appear.",
        "This number tells you exactly how many mines are touching that specific square",
        "in all 8 directions (top, bottom, left, right, and diagonals)."
        ""
    ]
    ruleStartY = app.height * 0.2
    lineSpacing = app.height * 0.04
    for i, line in enumerate(rules):
        drawLabel(line, 25, ruleStartY + i * lineSpacing, size=18, fill='white', align='left')
    
    getInstructionsBackButton(app).draw()

def instructions_onMousePress(app, mouseX, mouseY):
    if _isGuarded(app): return
    if getInstructionsBackButton(app).contains(mouseX, mouseY):
        switchScreen(app, 'start')

def instructions_onStep(app):
    app.screenGuard = False

def getCustomButtons(app):
    cx = app.width / 2
    spacing = app.height * 0.1
    firstRowY = app.height * 0.22
    pmBtnW, pmBtnH = 40, 30
    
    minus_btns = []
    plus_btns = []
    for i in range(3):
        rowY = firstRowY + i * spacing
        minus_btns.append(Button(cx - 100, rowY, pmBtnW, pmBtnH, "-", radius=5, textSize=24))
        plus_btns.append(Button(cx + 100, rowY, pmBtnW, pmBtnH, "+", radius=5, textSize=24))
    
    toggleY = firstRowY + 3 * spacing
    toggleW, toggleH = app.width * 0.35, app.height * 0.05
    noGuess = getattr(app, 'customNoGuess', True)
    toggleColor = rgb(100, 180, 100) if noGuess else rgb(180, 100, 100)
    toggleLabel = "No Guess Mode: ON" if noGuess else "No Guess Mode: OFF"
    toggleBtn = Button(cx, toggleY, toggleW, toggleH, toggleLabel, radius=8, fill=toggleColor, textSize=18, textFill='white')
    
    actionBtnW, actionBtnH = app.width * 0.21, app.height * 0.07
    playBtnY = toggleY + spacing * 0.8
    backBtnY = playBtnY + actionBtnH + app.height * 0.03
    playBtn = Button(cx, playBtnY + actionBtnH/2, actionBtnW, actionBtnH, "Play Custom")
    backBtn = Button(cx, backBtnY + actionBtnH/2, actionBtnW, actionBtnH, "Back")
    
    return minus_btns, plus_btns, toggleBtn, playBtn, backBtn

def custom_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(74, 117, 44))
    drawLabel("Custom Game Mode", app.width/2, app.height * 0.1, size=40, bold=True, fill='white')
    
    cx = app.width / 2
    spacing = app.height * 0.1
    firstRowY = app.height * 0.22
    
    for i, (label, value) in enumerate([("Rows", app.customRows), ("Cols", app.customCols), ("Mines", app.customMines)]):
        rowY = firstRowY + i * spacing
        drawLabel(f"{label}: {value}", cx, rowY, size=24, fill='white')
    
    minus_btns, plus_btns, toggleBtn, playBtn, backBtn = getCustomButtons(app)
    for btn in minus_btns + plus_btns:
        btn.draw()
    toggleBtn.draw()
    if getattr(app, 'customNoGuess', True):
        noteY = toggleBtn.cy + toggleBtn.height/2 + app.height * 0.025
        drawLabel("May be slow for large boards or high mine densities",
                  app.width/2, noteY, size=13, fill=rgb(255, 220, 120), italic=True)
    playBtn.draw()
    backBtn.draw()

def custom_onMousePress(app, mouseX, mouseY):
    if _isGuarded(app): return
    minus_btns, plus_btns, toggleBtn, playBtn, backBtn = getCustomButtons(app)
    
    for i in range(3):
        if minus_btns[i].contains(mouseX, mouseY):
            if i == 0: app.customRows = max(4, app.customRows - 1)
            elif i == 1: app.customCols = max(4, app.customCols - 1)
            elif i == 2: app.customMines = max(1, app.customMines - 1)
        elif plus_btns[i].contains(mouseX, mouseY):
            if i == 0: app.customRows = min(30, app.customRows + 1)
            elif i == 1: app.customCols = min(40, app.customCols + 1)
            elif i == 2: app.customMines = min(app.customRows * app.customCols - 1, app.customMines + 1)
    
    if toggleBtn.contains(mouseX, mouseY):
        app.customNoGuess = not getattr(app, 'customNoGuess', True)
    
    if playBtn.contains(mouseX, mouseY):
        app.customMines = min(app.customRows * app.customCols - 1, app.customMines)
        app.difficulties["Custom"] = (app.customRows, app.customCols, app.customMines)
        if "Custom" not in app.bestScores:
            app.bestScores["Custom"] = []
        app.currentDifficulty = "Custom"
        app.customConfigured = True
        # Set dimensions BEFORE restartApp so the board is created correctly
        app.rows = app.customRows
        app.cols = app.customCols
        app.numMines = app.customMines
        app.noGuessMode = app.customNoGuess
        restartApp(app)
        switchScreen(app, 'game')
    elif backBtn.contains(mouseX, mouseY):
        switchScreen(app, 'start')

def custom_onStep(app):
    app.screenGuard = False

def main():
    runAppWithScreens(initialScreen='start')

main()