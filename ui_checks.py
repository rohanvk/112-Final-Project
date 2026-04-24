from cmu_graphics import *
from game_engine import restartApp
from ui import getMenuButtonWidth

#This file is for checking whether something in the UI needs to change

def switchScreen(app, screenName):
    app.screenGuard = True
    setActiveScreen(screenName)

#ai helped implement this to prevent events from happening out of order
def _isGuarded(app):
    return getattr(app, 'screenGuard', False)

#if menu is hovered change the color
def checkMenuHover(app, mouseX, mouseY):
    if getattr(app, 'isDropdownOpen', False):
        menuOptX = app.menuX + app.menuShiftX
        menuOptTop = app.menuY + app.menuH
        menuOptBottom = menuOptTop + (app.menuH * len(app.difficulties))
        
        if menuOptX <= mouseX <= menuOptX + app.menuW and menuOptTop <= mouseY <= menuOptBottom:
            app.menuHoveredItem = (mouseY - menuOptTop) // app.menuH
        else:
            app.menuHoveredItem = None

def menuLogic(app, mouseX, mouseY):
    #used AI to help with this (dropdown menu)
    menuOptX = app.menuX + app.menuShiftX
    # Shift menu over
    menuOptTop = app.menuY + app.menuH
    menuOptBottom = menuOptTop + (app.menuH * len(app.difficulties))
    
    # Clicked option?
    if app.isDropdownOpen and menuOptX <= mouseX <= menuOptX + app.menuW and menuOptTop <= mouseY <= menuOptBottom:        
        itemIdx = int((mouseY - menuOptTop) // app.menuH)
        diffNames = list(app.difficulties.keys())
        if 0 <= itemIdx < len(diffNames):
            diffName = diffNames[itemIdx]
            if diffName == "Custom" and not getattr(app, 'customConfigured', False):
                app.isDropdownOpen = False
                return 'custom'
            app.currentDifficulty = diffName
            app.rows, app.cols, app.numMines = app.difficulties[diffName]
            if diffName == "Custom":
                app.noGuessMode = getattr(app, 'customNoGuess', True)
            else:
                app.noGuessMode = True
            restartApp(app)
        app.isDropdownOpen = False
        return True
    app.isDropdownOpen = False 
    # Clicked menu?
    btnW = getMenuButtonWidth(app)
    if app.menuX <= mouseX <= app.menuX + btnW and app.menuY <= mouseY <= app.menuY + app.menuH:
        app.isDropdownOpen = True
        return True

#check the lose and win screens at the end
def startOverButton(app, mouseX, mouseY):
    if app.gameOver:
        #dynamically resize the images so we dont lose the aspect ratio
        if app.isWin or app.endflag:
            tryScale = min((app.width * 0.6) / 1796, (app.height * 0.15) / 396)
            tryW, tryH = 1796 * tryScale, 396 * tryScale
            cx, cy = app.width / 2, app.height / 1.5
            #if you click the try again button, restart
            if (cx - tryW/2 <= mouseX <= cx + tryW/2) and (cy - tryH/2 <= mouseY <= cy + tryH/2):
                restartApp(app)
                return True
        elif not app.isWin and not app.endflag:
            # Fast-forward the remaining explosion wave if mouse pressed
            for r in range(app.rows):
                for c in range(app.cols):
                    cell = app.board[r][c]
                    if (cell.hasMine or cell.flagged) and cell.waveDelay > -1:
                        cell.waveDelay = 0
        return True

#checks if the autosolver button was pressed
def autoSolver(app,mouseX,mouseY):
    statusY = app.boardTop / 2
    btnW, btnH = 90, 30
    btnX = app.width * 0.75 - btnW/2
    btnY = statusY - btnH/2
    if btnX <= mouseX <= btnX + btnW and btnY <= mouseY <= btnY + btnH:
        app.autoSolve = not getattr(app, 'autoSolve', False)
        app.solverTarget = None
        return True
    return False

#checks if audio button was pressed
def checkAudioButton(app, mouseX, mouseY):
    statusY = app.boardTop / 2
    audioX = app.width - 80
    audioY = statusY
    audioR = 15
    if audioX - audioR <= mouseX <= audioX + audioR and audioY - audioR <= mouseY <= audioY + audioR:
        app.muted = not getattr(app, 'muted', False)
        return True
    return False

#check if the backbutton was pressed
def checkBackButton(app, mouseX, mouseY):
    statusY = app.boardTop / 2
    backX = app.width - 30
    backY = statusY
    backR = 15
    if ((mouseX - backX)**2 + (mouseY - backY)**2)**0.5 <= backR:
        app.autoSolve = False
        return 'start'
    return False
