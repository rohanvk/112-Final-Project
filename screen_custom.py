from cmu_graphics import *
from button import Button
from ui_checks import switchScreen, _isGuarded
from game_engine import restartApp, getSafeZoneSize

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
        if i == 2 and getattr(app, '_mineInputActive', False):
            # Draw editable mine input with cursor
            inputText = getattr(app, '_mineInputText', str(app.customMines))
            boxW = max(120, len(f"Mines: {inputText}|") * 13)
            drawRect(cx - boxW/2, rowY - 16, boxW, 32, fill=rgb(50, 80, 35), border='white', borderWidth=2)
            drawLabel(f"Mines: {inputText}|", cx, rowY, size=24, fill='white')
        else:
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

def _maxMines(rows, cols):
    return rows * cols - getSafeZoneSize(rows, cols)

def custom_onMousePress(app, mouseX, mouseY):
    if _isGuarded(app): return
    minus_btns, plus_btns, toggleBtn, playBtn, backBtn = getCustomButtons(app)
    
    # Check if clicking the mine count label to type a value
    cx = app.width / 2
    spacing = app.height * 0.1
    firstRowY = app.height * 0.22
    mineRowY = firstRowY + 2 * spacing
    if cx - 50 <= mouseX <= cx + 50 and mineRowY - 16 <= mouseY <= mineRowY + 16:
        app._mineInputActive = True
        app._mineInputText = str(app.customMines)
        return
    elif getattr(app, '_mineInputActive', False):
        _confirmMineInput(app)
    
    for i in range(3):
        if minus_btns[i].contains(mouseX, mouseY):
            if i == 0: 
                app.customRows = max(4, app.customRows - 1)
                app.customMines = max(1, int(app.customRows * app.customCols * 0.2))
            elif i == 1: 
                app.customCols = max(4, app.customCols - 1)
                app.customMines = max(1, int(app.customRows * app.customCols * 0.2))
            elif i == 2: 
                app.customMines = max(1, app.customMines - 1)
        elif plus_btns[i].contains(mouseX, mouseY):
            if i == 0: 
                app.customRows = min(30, app.customRows + 1)
                app.customMines = max(1, int(app.customRows * app.customCols * 0.2))
            elif i == 1: 
                app.customCols = min(40, app.customCols + 1)
                app.customMines = max(1, int(app.customRows * app.customCols * 0.2))
            elif i == 2: 
                app.customMines = min(_maxMines(app.customRows, app.customCols), app.customMines + 1)
    
    # Cap mines to safe zone limit after any row/col change
    app.customMines = min(app.customMines, _maxMines(app.customRows, app.customCols))
    
    if toggleBtn.contains(mouseX, mouseY):
        app.customNoGuess = not getattr(app, 'customNoGuess', True)
        app._noGuessAutoDisabled = False  # Manual toggle clears auto-disable flag
    
    # Auto-manage no-guess mode based on mine density
    totalCells = app.customRows * app.customCols
    if app.customMines > totalCells * 0.5:
        # Force no-guess off at high density
        if app.customNoGuess:
            app.customNoGuess = False
            app._noGuessAutoDisabled = True
    elif getattr(app, '_noGuessAutoDisabled', False):
        # Re-enable if it was auto-disabled (not manually turned off)
        app.customNoGuess = True
        app._noGuessAutoDisabled = False
    
    if playBtn.contains(mouseX, mouseY):
        app.customMines = min(_maxMines(app.customRows, app.customCols), app.customMines)
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

def custom_onKeyPress(app, key):
    if not getattr(app, '_mineInputActive', False):
        return
    
    text = getattr(app, '_mineInputText', '')
    
    if key == 'enter':
        _confirmMineInput(app)
    elif key == 'escape':
        app._mineInputActive = False
    elif key == 'backspace':
        app._mineInputText = text[:-1]
    elif key.isdigit():
        # Cap at 4 digits to prevent huge numbers
        if len(text) < 4:
            app._mineInputText = text + key

def _confirmMineInput(app):
    text = getattr(app, '_mineInputText', '')
    app._mineInputActive = False
    if text and text.isdigit():
        value = int(text)
        value = max(1, min(value, _maxMines(app.customRows, app.customCols)))
        app.customMines = value
        
        # Apply no-guess density check
        totalCells = app.customRows * app.customCols
        if app.customMines > totalCells * 0.5:
            if getattr(app, 'customNoGuess', True):
                app.customNoGuess = False
                app._noGuessAutoDisabled = True
        elif getattr(app, '_noGuessAutoDisabled', False):
            app.customNoGuess = True
            app._noGuessAutoDisabled = False
