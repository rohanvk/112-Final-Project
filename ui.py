from cmu_graphics import *
from board import *

def drawTimer(app):
    timer = 0 if app.firstClick else app.timer
    drawLabel(f'{pythonRound(timer, 1)}', app.width/2 + 85, 45 ,align='left', size=24, fill ='white')
    drawImage(app.timerimage, app.width/2 + 50, 45, align = 'center')

def drawStatus(app):
    flagsPlaced = 0
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col].flagged:
                flagsPlaced += 1
    
    minesLeft = app.numMines - flagsPlaced
    
    # Display the mines left
    drawLabel(minesLeft, app.width/2, 45, size=24, align='right', fill='white')
    drawImage(app.flagImage, app.width/2 - 55, 45, align='center', width=40,height=40 )
    
    # Display no guess mode status
    if getattr(app, 'noGuessMode', True) == False:
        drawLabel("no guess mode off", app.width/2, 75, align='center', size=12, fill='red', bold=True)
        
    # Auto Solve Button
    btnW, btnH = 90, 30
    btnX = app.width - btnW - 20
    btnY = 30
    if getattr(app, 'autoSolve', False):
        fillColor = rgb(200, 200, 200)
    else:
        fillColor = 'white'
    drawRoundedRect(btnX, btnY, btnW, btnH, radius=5, fill=fillColor, border=fillColor)
    drawLabel("Auto Solve", btnX + btnW/2, btnY + btnH/2, size=14, bold=True)

def drawCells(app):
    cellW = app.boardWidth / app.cols
    cellH = app.boardHeight / app.rows

    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            l = app.boardLeft + col * cellW
            t = app.boardTop + row * cellH
            
            cx = l + cellW/2
            cy = t + cellH/2
            
            if cell.revealed:
                if cell.hasMine:
                    # mines
                    # get random index for mines
                    colorIndex = (row * 11 + col * 17) % 8 + 1
                    mineBgColor, mineCircleColor = app.numberColors[colorIndex]
                    
                    # background = light color
                    drawRect(l, t, cellW, cellH, fill=mineBgColor)
                    
                    # center = dark color
                    radius = min(cellW, cellH) * 0.25
                    drawCircle(cx, cy, radius, fill=mineCircleColor)
                else:
                    # dirt checker
                    if (row + col) % 2 == 0:
                        dirtColor = rgb(229, 194, 159)
                    else:
                        dirtColor = rgb(215, 184, 153)
                    
                    drawRect(l, t, cellW, cellH, fill=dirtColor)
                    
                    if cell.adjacentMines > 0:
                        # Get color for num
                        numColor = app.textColors[cell.adjacentMines]
                        drawLabel(cell.adjacentMines, cx, cy, size=cellW*0.8, bold=True, fill=numColor, font='arial')
                        
                if getattr(app, 'solverTarget', None) == (row, col):
                    drawCircle(cx, cy, min(cellW, cellH) * 0.25, fill=rgb(150, 150, 150), opacity=70)
            else:
                # grass checker
                if (row + col) % 2 == 0:
                    baseColor = rgb(170, 215, 81)  # Light grass
                else:
                    baseColor = rgb(162, 209, 73)  # Dark grass
                
                # hover / win flash color / solver target
                isFlashing = getattr(app, 'winFlashTimer', 0) > 0
                if app.hoveredCell == (row, col) or getattr(app, 'solverTarget', None) == (row, col) or isFlashing:
                    cellColor = rgb(191, 225, 125) # Hover / Flash color
                else:
                    cellColor = baseColor
                
                drawRect(l, t, cellW, cellH, fill=cellColor)
                
                if getattr(app, 'solverTarget', None) == (row, col):
                    drawCircle(cx, cy, min(cellW, cellH) * 0.25, fill=rgb(150, 150, 150), opacity=70)
                
                if cell.flagged:
                    if cell.flagScale > 0:
                        sw = cellW * 0.8 * cell.flagScale
                        sh = cellH * 0.8 * cell.flagScale
                        drawImage(app.flagImage, cx, cy, align='center',width=sw, height=sh)

    # Loop 2 to draw an edge between the borders of the grass and opened cells, ai assisted
    edgeColor = rgb(135, 175, 58)
    edgeThickness = 2
    
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            
            if cell.revealed:
                l = app.boardLeft + col * cellW
                t = app.boardTop + row * cellH
                
                # if top
                if row > 0 and not app.board[row-1][col].revealed:
                    drawLine(l, t, l + cellW, t, fill=edgeColor, lineWidth=edgeThickness)
                
                # if bottom
                if row < app.rows - 1 and not app.board[row+1][col].revealed:
                    drawLine(l, t + cellH, l + cellW, t + cellH, fill=edgeColor, lineWidth=edgeThickness)
                
                # if left
                if col > 0 and not app.board[row][col-1].revealed:
                    drawLine(l, t, l, t + cellH, fill=edgeColor, lineWidth=edgeThickness)
                
                # if right
                if col < app.cols - 1 and not app.board[row][col+1].revealed:
                    drawLine(l + cellW, t, l + cellW, t + cellH, fill=edgeColor, lineWidth=edgeThickness)

    # animation loop, used ai for this
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            
            if cell.isAnimating:
                l = app.boardLeft + col * cellW
                t = app.boardTop + row * cellH
                
                # get size
                animW = cellW * cell.animScale
                animH = cellH * cell.animScale
                
                # randomly move
                acx = l + cellW/2 + cell.animOffsetX
                acy = t + cellH/2 + cell.animOffsetY
                
                # get new location
                animL = acx - animW/2
                animT = acy - animH/2
                
                # get color
                isFlashing = getattr(app, 'winFlashTimer', 0) > 0
                if app.hoveredCell == (row, col) or getattr(app, 'solverTarget', None) == (row, col) or isFlashing:
                    grassColor = rgb(191, 225, 125) # Flash / Hover effect
                elif (row + col) % 2 == 0:
                    grassColor = rgb(170, 215, 81)  # Light grass
                else:
                    grassColor = rgb(162, 209, 73)  # Dark grass
                
                drawRect(animL, animT, animW, animH, fill=grassColor)

            if cell.isFlagDespawning: #similar logic for the flags
                if cell.flagDespawnScale > 0.01: #cmu graphics hates 0
                    l = app.boardLeft + col * cellW
                    t = app.boardTop + row * cellH
                    
                    sw = cellW * 0.8 * cell.flagDespawnScale
                    sh = cellH * 0.8 * cell.flagDespawnScale
                    fcx = l + cellW/2 + cell.flagDespawnOffsetX
                    fcy = t + cellH/2 + cell.flagDespawnOffsetY
                    
                    drawImage(app.flagImage, fcx, fcy, align='center', width=sw, height=sh)

def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            color = 'lightGray'
            drawCell(app, row, col,color)

def drawCell(app, row, col, color):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    drawRect(cellLeft, cellTop, cellWidth, cellHeight,
             fill=color, border=None,
             borderWidth=app.cellBorderWidth)

    
def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)

def resizeBoard(app, numRows, numCols, boardSize):
    app.rows = numRows
    app.cols = numCols
    app.boardLeft, app.boardWidth, app.boardHeight = boardSize
    app.board = [[Cell(row, col) for col in range (app.cols)] for row in range(app.rows)]

def drawRoundedRect(x, y, w, h, radius, fill='black', border=None, borderWidth=1):
    # Used AI to make this function, draws 4 circles and two rectangles
    drawRect(x + radius, y, w - 2 * radius, h, fill=fill)
    drawRect(x, y + radius, w, h - 2 * radius, fill=fill)
    
    drawCircle(x + radius, y + radius, radius, fill=fill)
    drawCircle(x + w - radius, y + radius, radius, fill=fill)
    drawCircle(x + radius, y + h - radius, radius, fill=fill)
    drawCircle(x + w - radius, y + h - radius, radius, fill=fill)
    
    # Outlines rectangles
    if border != None:
        # Edges
        drawLine(x + radius, y, x + w - radius, y, fill=border, lineWidth=borderWidth) # Top
        drawLine(x + radius, y + h, x + w - radius, y + h, fill=border, lineWidth=borderWidth) # Bottom
        drawLine(x, y + radius, x, y + h - radius, fill=border, lineWidth=borderWidth) # Left
        drawLine(x + w, y + radius, x + w, y + h - radius, fill=border, lineWidth=borderWidth) # Right
        
        # Arcs
        d = radius * 2
        drawArc(x + w - radius, y + radius, d, d, 0, 90, fill=None, border=border, borderWidth=borderWidth) # Top-Right
        drawArc(x + radius, y + radius, d, d, 90, 90, fill=None, border=border, borderWidth=borderWidth) # Top-Left
        drawArc(x + radius, y + h - radius, d, d, 180, 90, fill=None, border=border, borderWidth=borderWidth) # Bottom-Left
        drawArc(x + w - radius, y + h - radius, d, d, 270, 90, fill=None, border=border, borderWidth=borderWidth) # Bottom-Right

def getMenuButtonWidth(app):
    #dynamic button sizing in the menu
    return 10 + len(app.currentDifficulty) * 10 + 30

def drawMenu(app):
    #Draw menu, used some ai here
    btnW = getMenuButtonWidth(app)
    drawRoundedRect(app.menuX, app.menuY, btnW, app.menuH, radius=6, fill='white', border='white', borderWidth=1)
    
    drawLabel(app.currentDifficulty, app.menuX + 10, app.menuY + app.menuH/2, 
              fill='black', bold=True, size=16, font='arial', align='left')

    #draw arrow image
    arrowSize = 12
    drawImage(app.downArrow, app.menuX + btnW - 20, app.menuY + app.menuH/2, 
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
        itemIdx = (mouseY - menuOptTop) // app.menuH       
        for i, diffName in enumerate(app.difficulties.keys()):
            if i == itemIdx:
                app.currentDifficulty = diffName
                app.rows, app.cols, app.numMines = app.difficulties[diffName]
                restartApp(app)
        return True
    app.isDropdownOpen = False 
    # Clicked menu?
    btnW = getMenuButtonWidth(app)
    if app.menuX <= mouseX <= app.menuX + btnW and app.menuY <= mouseY <= app.menuY + app.menuH:
        app.isDropdownOpen = True
        return True

def startOverButton(app, mouseX, mouseY):
    if app.gameOver:
        if app.isWin or app.endflag:
            tryScale = min((app.width * 0.6) / 1796, (app.height * 0.15) / 396)
            tryW, tryH = 1796 * tryScale, 396 * tryScale
            cx, cy = app.width / 2, app.height / 1.5
            if (cx - tryW/2 <= mouseX <= cx + tryW/2) and (cy - tryH/2 <= mouseY <= cy + tryH/2):
                restartApp(app)
                return True
        elif not app.isWin and not app.endflag:
            # Fast-forward the remaining explosion wave
            for r in range(app.rows):
                for c in range(app.cols):
                    cell = app.board[r][c]
                    if (cell.hasMine or cell.flagged) and cell.waveDelay > -1:
                        cell.waveDelay = 0
        return True


def drawGameScreens(app):
    if not app.gameOver: return
    
    # Calculate scale for images (used ai for this). 
    # Hard coded: 1323x991 (aim for max 70% width or 55% height)
    wlScale = min((app.width * 0.7) / 1323, (app.height * 0.55) / 991)
    wlW, wlH = 1323 * wlScale, 991 * wlScale
    
    # Try Again button hard code: 1796x396
    tryScale = min((app.width * 0.6) / 1796, (app.height * 0.15) / 396)
    tryW, tryH = 1796 * tryScale, 396 * tryScale
    
    # draw win screen
    if checkWin(app) or app.forcedWin:
        drawRect(0,0,app.width,app.height,fill='slategray',opacity=50)
        drawImage(app.winimage, app.width/2, app.height/3, width=wlW, height=wlH, align='center')
        drawImage(app.tryagain, app.width/2, app.height/(3/2), width=tryW, height=tryH, align='center')

    #draw lose screen
    elif app.endflag:
        drawRect(0,0,app.width,app.height,fill='slategray',opacity=50)
        drawImage(app.loseimage, app.width/2, app.height/3, width=wlW, height=wlH, align='center')
        drawImage(app.tryagain, app.width/2, app.height/(3/2), width=tryW, height=tryH, align='center')

    # draw counters over the images if win or lose screen is shown
    if checkWin(app) or app.endflag or app.forcedWin:
        bestList = app.bestScores[app.currentDifficulty]
        bestText = str(bestList[0]) if len(bestList) > 0 else "-"
        currText = str(app.timer)
        
        # Left side: current time
        drawLabel(currText, app.width/2 - wlW*0.25, app.height/3 + wlH*0.05, size=32, bold=True, fill='white', align='left')
        # Right side: best time 
        drawLabel(bestText, app.width/2 + wlW*0.20, app.height/3 + wlH*0.05, size=32, bold=True, fill='white', align='left')
