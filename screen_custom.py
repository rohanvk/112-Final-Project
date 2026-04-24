from cmu_graphics import *
from button import Button
from ui_checks import switchScreen, _isGuarded
from game_engine import restartApp

#Handles screens for the board customization screen

#AI helped fix errors here
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
    
    #Enumerate, was very helpful to get this in lecture lol
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
        # Set dimensions
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
