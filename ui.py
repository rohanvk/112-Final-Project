from cmu_graphics import *
from board import *
#this file is pretty self explanatory 

def drawTimer(app):
    timer = 0 if app.firstClick else app.timer
    statusY = app.boardTop / 2
    drawLabel(f'{pythonRound(timer, 1)}', app.width/2 + 85, statusY ,align='left', size=24, fill ='white')
    drawImage(app.timerimage, app.width/2 + 50, statusY, align = 'center')

#draw flags left and mines
def drawStatus(app):
    flagsPlaced = 0
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col].flagged:
                flagsPlaced += 1
    
    minesLeft = app.numMines - flagsPlaced
    statusY = app.boardTop / 2
    
    # mines left
    drawLabel(minesLeft, app.width/2, statusY, size=24, align='right', fill='white')
    drawImage(app.flagImage, app.width/2 - 55, statusY, align='center', width=40,height=40 )
    
    # no guess mode status
    if getattr(app, 'noGuessMode', True) == False:
        drawLabel("no guess mode off", app.width/2, statusY + 30, align='center', size=12, fill='red', bold=True)
        
    # Autosolve button (used some ai for the spacing)
    btnW, btnH = 80, 30
    btnX = app.width * 0.75 - btnW/2
    btnY = statusY - btnH/2
    if getattr(app, 'autoSolve', False):
        fillColor = rgb(200, 200, 200)
    else:
        fillColor = 'white'
    drawRoundedRect(btnX, btnY, btnW, btnH, radius=5, fill=fillColor, border=fillColor)
    drawLabel("Auto Solve", btnX + btnW/2, btnY + btnH/2, size=14, bold=True)
    
    # Audio button/image
    audioX = app.width - 80
    audioY = statusY
    audioR = 15
    if getattr(app, 'audioImage', None):
        drawImage(app.audioImage, audioX, audioY, align='center', width=audioR*2, height=audioR*2)
    else:
        drawRect(audioX-audioR, audioY-audioR, audioR*2, audioR*2, fill='gray')
    if getattr(app, 'muted', False):
        drawLine(audioX - audioR, audioY - audioR, audioX + audioR, audioY + audioR, fill='red', lineWidth=3)
        
    # X button (Back to Start)
    backX = app.width - 30
    backY = statusY
    backR = 15
    drawLabel("X", backX, backY, fill='white', bold=True, size=28)

def drawCells(app):
    cellW = app.boardWidth / app.cols
    cellH = app.boardHeight / app.rows
    baseFlagSize = min(cellW, cellH) * 0.8

    #draw the cells
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            l = app.boardLeft + col * cellW
            t = app.boardTop + row * cellH
            
            cx = l + cellW/2
            cy = t + cellH/2
            
            #draw the mines
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
                
                #draw the dirt (opened cells)
                else:
                    # dirt checker pattern
                    if (row + col) % 2 == 0:
                        dirtColor = rgb(229, 194, 159)
                    else:
                        dirtColor = rgb(215, 184, 153)
                    
                    drawRect(l, t, cellW, cellH, fill=dirtColor)
                    
                    if cell.adjacentMines > 0:
                        # Get color for num
                        numColor = app.textColors[cell.adjacentMines]
                        drawLabel(cell.adjacentMines, cx, cy, size=cellW*0.8, bold=True, fill=numColor, font='arial')
                 #used ai for this, draws a circle on the targeted solver cell       
                if getattr(app, 'solverTarget', None) == (row, col):
                    drawCircle(cx, cy, min(cellW, cellH) * 0.25, fill=rgb(150, 150, 150), opacity=70)
            
            #draw the grass
            else:
                # grass checker pattern
                if (row + col) % 2 == 0:
                    baseColor = rgb(170, 215, 81)  # Light grass
                else:
                    baseColor = rgb(162, 209, 73)  # Dark grass
                
                # hover / win flash color / solver target
                isFlashing = getattr(app, 'winFlashTimer', 0) > 0
                if app.hoveredCell == (row, col) or getattr(app, 'solverTarget', None) == (row, col) or isFlashing:
                    cellColor = rgb(191, 225, 125) # Hover / flash / target color
                else:
                    cellColor = baseColor
                
                drawRect(l, t, cellW, cellH, fill=cellColor)
                
                if getattr(app, 'solverTarget', None) == (row, col):
                    drawCircle(cx, cy, min(cellW, cellH) * 0.25, fill=rgb(150, 150, 150), opacity=70)
                
                #draw the flags
                if cell.flagged:
                    if cell.flagScale > 0:
                        sw = baseFlagSize * cell.flagScale
                        sh = baseFlagSize * cell.flagScale
                        drawImage(app.flagImage, cx, cy, align='center',width=sw, height=sh)

    # draw a continuous edge between the borders of the grass and opened cells, ai assisted
    edgeColor = rgb(135, 175, 58)
    edgeThickness = 2
    
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            
            #on open cells add an edge between not opened cells
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
            
            #grass animation
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
                    
                    sw = baseFlagSize * cell.flagDespawnScale
                    sh = baseFlagSize * cell.flagDespawnScale
                    fcx = l + cellW/2 + cell.flagDespawnOffsetX
                    fcy = t + cellH/2 + cell.flagDespawnOffsetY
                    
                    drawImage(app.flagImage, fcx, fcy, align='center', width=sw, height=sh, rotateAngle=cell.flagDespawnRotation)

#add a slight backdrop
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
        
        # Arcs (possibly a small bug here?)
        d = radius * 2
        drawArc(x + w - radius, y + radius, d, d, 0, 90, fill=None, border=border, borderWidth=borderWidth) # Top-Right
        drawArc(x + radius, y + radius, d, d, 90, 90, fill=None, border=border, borderWidth=borderWidth) # Top-Left
        drawArc(x + radius, y + h - radius, d, d, 180, 90, fill=None, border=border, borderWidth=borderWidth) # Bottom-Left
        drawArc(x + w - radius, y + h - radius, d, d, 270, 90, fill=None, border=border, borderWidth=borderWidth) # Bottom-Right

#changes size based on option selected
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

#draw the end game screens
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
    if app.isWin:
        drawRect(0,0,app.width,app.height,fill='slategray',opacity=50)
        drawImage(app.winimage, app.width/2, app.height/3, width=wlW, height=wlH, align='center')
        drawImage(app.tryagain, app.width/2, app.height/(3/2), width=tryW, height=tryH, align='center')

    #draw lose screen
    elif app.endflag:
        drawRect(0,0,app.width,app.height,fill='slategray',opacity=50)
        drawImage(app.loseimage, app.width/2, app.height/3, width=wlW, height=wlH, align='center')
        drawImage(app.tryagain, app.width/2, app.height/(3/2), width=tryW, height=tryH, align='center')

    # draw counters over the images if win or lose screen is shown
    if app.isWin or app.endflag:
        bestList = app.bestScores[app.currentDifficulty]
        bestText = str(bestList[0]) if len(bestList) > 0 else "-"
        currText = str(app.timer)
        
        # Left side: current time
        drawLabel(currText, app.width/2 - wlW*0.25, app.height/3 + wlH*0.05, size=32, bold=True, fill='white', align='left')
        # Right side: best time 
        drawLabel(bestText, app.width/2 + wlW*0.20, app.height/3 + wlH*0.05, size=32, bold=True, fill='white', align='left')
