#For all citations of AI, Gemini Pro 3.1 was used

from cmu_graphics import *
from PIL import Image as PILImage
import time #need because otherwise timer tracks framerate
from board import *
from ui import *
from solver import *

def onAppStart(app):
    app.width = app.height = 750
    app.stepsPerSecond = 20
    app.rows = 25
    app.cols = 21
    app.boardLeft = 10
    app.boardTop = 100
    app.boardWidth = 600
    app.boardHeight = 650
    app.cellBorderWidth = 0.5
    app.paused = False
    app.board = [[Cell(row, col) for col in range (app.cols)] for row in range(app.rows)]
    app.score = 0
    app.gameOver = False
    app.prob = 0.3
    app.firstClick = True
    app.startTime = time.time()
    app.timer = 1
    app.hoveredCell = None
    app.confetti = []
    app.bestScores = []
    app.winFlashTimer = 0
    app.isDropdownOpen = False
    app.menuHoveredItem = None
    app.currentDifficulty = "Medium"
    app.menuShiftX = 15       
    app.checkmarkIndentX = 30
    app.difficulties = {
        "Easy": (8, 10, 10),
        "Medium": (14, 18, 40),
        "Hard": (20, 24, 99)
    }
    
    # Menu location and size
    app.menuX = 20
    app.menuY = 15
    app.menuW = 120
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

def restartApp(app):
    app.paused = False
    app.board = [[Cell(row, col) for col in range (app.cols)] for row in range(app.rows)]
    app.score = 0
    app.gameOver = False
    app.firstClick = True
    app.timer = 1
    app.startTime = time.time()
    app.confetti = []


def onMouseMove(app, mouseX, mouseY):
    if app.gameOver:
        app.hoveredCell = None
        return
        
    coords = getCell(app, mouseX, mouseY)
    
    if app.hoveredCell != coords:
        app.hoveredCell = coords

    #used some ai to get the hover for the menu
    if getattr(app, 'isDropdownOpen', False):
            menuOptX = app.menuX + app.menuShiftX
            menuOptTop = app.menuY + app.menuH
            menuOptBottom = menuOptTop + (app.menuH * len(app.difficulties))
            
            if menuOptX <= mouseX <= menuOptX + app.menuW and menuOptTop <= mouseY <= menuOptBottom:
                app.menuHoveredItem = (mouseY - menuOptTop) // app.menuH
            else:
                app.menuHoveredItem = None

def onMousePress(app, mouseX, mouseY, button):
    #used AI to help with this (dropdown menu)
    menuOptX = app.menuX + app.menuShiftX
    # Shift menu over
    menuOptTop = app.menuY + app.menuH
    menuOptBottom = menuOptTop + (app.menuH * len(app.difficulties))
    
    # Clicked option?
    if menuOptX <= mouseX <= menuOptX + app.menuW and menuOptTop <= mouseY <= menuOptBottom:        
        itemIdx = (mouseY - menuOptTop) // app.menuH        
        for i, diffName in enumerate(app.difficulties.keys()):
            if i == itemIdx:
                app.currentDifficulty = diffName
                app.rows, app.cols, app.numMines = app.difficulties[diffName]
                restartApp(app)
        return
    app.isDropdownOpen = False 
    # Clicked menu?
    if app.menuX <= mouseX <= app.menuX + app.menuW and app.menuY <= mouseY <= app.menuY + app.menuH:
        app.isDropdownOpen = True
        return
    if app.gameOver: return

    coords = getCell(app, mouseX, mouseY)
    if coords is None: return
    row, col = coords
    cell = app.board[row][col]

    # Right Click
    if button == 2:
        if not cell.revealed:
            if cell.flagged: # remove flag
                cell.isFlagDespawning = True
                cell.flagDespawnScale = 1.0
                cell.flagDespawnOffsetX = 0
                cell.flagDespawnOffsetY = 0
            #pop up and then out
            cell.flagDespawnDy = random.randint(-12, -8) 
            cell.flagDespawnDx = random.randint(-4, 4)

            cell.flagged = not cell.flagged

            if cell.flagged: #add flag
                cell.isFlagAnimating = True
                cell.flagScale = 0.1

    # Left Click
    elif button == 0:
        if cell.flagged: return 
        
        if app.firstClick:
            placeMines(app, row, col)
            app.firstClick = False

        if cell.hasMine:
            app.gameOver = True
            app.isWin = False

            cell.revealed = True

            for r in range(app.rows):
                for c in range(app.cols):
                    checkCell = app.board[r][c]
                    if r-row == 0 and c - col == 0:
                        checkCell.waveDelay = 1
                    if (checkCell.hasMine or checkCell.flagged) and not checkCell.revealed:
                        dist = ((r - row)**2 + (c - col)**2)**0.5
                        checkCell.waveDelay = int(dist * 12)

        else:
            revealCell(app, row,col)
            
            if checkWin(app):
                app.gameOver = True
                app.isWin = True
                app.winFlashTimer = 15
                
                # Save score
                app.bestScores.append(app.timer)
                app.bestScores.sort()
                
                # Pop all flags and generate confetti
                app.confetti = []
                confettiColors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
                
                for r in range(app.rows):
                    for c in range(app.cols):
                        checkCell = app.board[r][c]
                        if checkCell.flagged:
                            checkCell.flagged = False
                            checkCell.isFlagDespawning = True
                            checkCell.flagDespawnScale = 1.0
                            checkCell.flagDespawnOffsetX = 0
                            checkCell.flagDespawnOffsetY = 0
                            checkCell.flagDespawnDy = random.randint(-12, -8)
                            checkCell.flagDespawnDx = random.randint(-4, 4)
                            
                for i in range(150):
                    app.confetti.append({
                        'x': random.randint(0, app.width),
                        'y': random.randint(-300, -50),
                        'dx': random.randint(-6, 6),
                        'dy': random.randint(2, 12),
                        'size': random.randint(6, 12),
                        'color': random.choice(confettiColors)
                    })        

def onKeyPress(app, key):
    if app.gameOver:
        restartApp(app)
    else:
        if key == 'p': 
            app.paused = not app.paused
        elif key == 'r': 
            restartApp(app)

def onStep(app):
    if not app.paused and not app.gameOver:
        takeStep(app)
        #animation!
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            
            # if cell animating, change animation
            if cell.isAnimating:
                cell.animScale -= 0.11     # Shrink by 10% every frame
                cell.animOffsetX += cell.animDx # Move X
                cell.animOffsetY += cell.animDy # Move Y
                
                # stop animation
                if cell.animScale <= 0:
                    cell.animScale = 0
                    cell.isAnimating = False
            if cell.isFlagAnimating:
                cell.flagScale += 0.4  # Increase size by 20% per frame
                if cell.flagScale >= 1.0:
                    cell.flagScale = 1.0
                    cell.isFlagAnimating = False

            if cell.isFlagDespawning:
                gravity = 1.2
                cell.flagDespawnDy += gravity
                cell.flagDespawnOffsetX += cell.flagDespawnDx
                cell.flagDespawnOffsetY += cell.flagDespawnDy

                if cell.flagDespawnDy > 0:
                    cell.flagDespawnScale -= 0.1
                if cell.flagDespawnScale <= 0:
                    cell.flagDespawnScale = 0
                    cell.isFlagDespawning = False
    if app.gameOver:
        if not app.isWin:
            # lose = mines explode
            for r in range(app.rows):
                for c in range(app.cols):
                    cell = app.board[r][c]
                    if (cell.hasMine or cell.flagged) and cell.waveDelay > 0:
                        cell.waveDelay -= 1
                        if cell.waveDelay <= 0:
                            if cell.flagged:
                                cell.flagged = False
                                cell.isFlagDespawning = True
                                cell.flagDespawnScale = 1.0
                                cell.flagDespawnOffsetX = 0
                                cell.flagDespawnOffsetY = 0
                                cell.flagDespawnDy = random.uniform(-18, -10)
                                cell.flagDespawnDx = random.uniform(-10, 10)
                            if cell.hasMine:
                                cell.revealed = True
                                cell.isAnimating = True
                                cell.animScale = 1.0
                                cell.animOffsetX = 0
                                cell.animOffsetY = 0
                                cell.animDx = random.choice([-1, 1]) * random.randint(3, 8)
                                cell.animDy = random.choice([-1, 1]) * random.randint(3, 8)

                                # get unique color
                                colorIndex = (r * 11 + c * 17) % 8 + 1
                                mineBgColor, _ = app.numberColors[colorIndex]
                                # get cell center
                                l, t = getCellLeftTop(app, r, c)
                                w, h = getCellSize(app)
                                cx, cy = l + w/2, t + h/2
                                if not hasattr(app, 'confetti'): app.confetti = [] # make sure we have app.confetti
                                # add 8 particles for loss
                                for _ in range(8):
                                    app.confetti.append({
                                        'x': cx,
                                        'y': cy,
                                        # Go UP (Dy is negative)
                                        'dy': random.uniform(-4, -3), 
                                        # Sideways
                                        'dx': random.uniform(-5, 5),    
                                        'size': random.randint(9, 10),
                                        # Use unique colors
                                        'color': mineBgColor 
                                    })
        else:
            # used ai for this, flashes screen and does confetti
            if app.winFlashTimer > 0:
                app.winFlashTimer -= 1
                
            for p in app.confetti:
                p['dy'] += 0.2
                p['x'] += p['dx']
                p['y'] += p['dy']
                if p['dx'] > 0: p['dx'] -= 0.1
                elif p['dx'] < 0: p['dx'] += 0.1

        for p in getattr(app, 'confetti', []): #used ai for this part to get confetti during end
            p['dy'] += 0.2              # Gravity
            # Flutter effect
            if p['dx'] > 0: p['dx'] -= 0.05
            elif p['dx'] < 0: p['dx'] += 0.05
            
            # Move across screen
            p['x'] += p['dx']
            p['y'] += p['dy']

def takeStep(app):
    app.timer = int(time.time() - app.startTime)

def redrawAll(app):

    drawRect(0, 0, app.width, app.height, fill='darkGray') # Background
    drawStatus(app)
    drawBoard(app)
    drawBoardBorder(app)
    drawTimer(app)
    drawCells(app)
    if app.gameOver:
        for p in app.confetti:
            # Only draw it if it's on the screen
            if p['y'] < app.height:
                drawRect(p['x'], p['y'], p['size'], p['size'], fill=p['color'], align='center')

    #Draw menu, used some ai here
    drawRoundedRect(app.menuX, app.menuY, app.menuW, app.menuH, radius=6, fill='white', border='white', borderWidth=1)
    
    drawLabel(app.currentDifficulty, app.menuX + app.checkmarkIndentX, app.menuY + app.menuH/2, 
              fill='black', bold=True, size=16, font='arial', align='left')

    #draw arrow image
    arrowSize = 12
    drawImage(app.downArrow, app.menuX + app.menuW - 20, app.menuY + app.menuH/2, 
              align='center', width=arrowSize, height=arrowSize)
    
    # draw options if open
    if app.isDropdownOpen:
        # shift dropdowns right
        menuOptX = app.menuX + app.menuShiftX
        
        shadowOffset = 3
        numItems = len(app.difficulties)
        
        drawRoundedRect(menuOptX + shadowOffset, app.menuY + app.menuH + shadowOffset, 
                        app.menuW, app.menuH * numItems, radius=6, fill='gray')
        
        drawRoundedRect(menuOptX, app.menuY + app.menuH, 
                        app.menuW, app.menuH * numItems, radius=6, fill='white')
        
        # Draw each option
        for i, diffName in enumerate(app.difficulties.keys()):
            optY = app.menuY + app.menuH + (app.menuH * i)
            
            bgColor = 'white'
            
            # Change on hover
            if getattr(app, 'menuHoveredItem', None) == i:
                bgColor = rgb(235, 235, 235)
            
            drawRoundedRect(menuOptX, optY, app.menuW, app.menuH, radius=6, fill=bgColor, border=None)
            
            # checkmark on option selected
            if diffName == app.currentDifficulty:
                drawImage(app.checkmark, menuOptX + 15, optY + app.menuH/2, align='center', width=20, height=25)
            
            drawLabel(diffName, menuOptX + app.checkmarkIndentX, optY + app.menuH/2, 
                      fill='black', bold=True, size=16, font='arial', align='left')
def main():
    runApp()

main()