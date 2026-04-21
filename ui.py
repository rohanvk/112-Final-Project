from cmu_graphics import *
from board import *

def drawTimer(app):
    drawOval(app.width-25, 50, 150, 50, fill='lightblue', align='right')
    timer = 0 if app.firstClick else app.timer
    drawLabel(f'Timer: {pythonRound(timer, 1)}', app.width-150, 50,align='left', size=20)

def drawStatus(app):
    pass

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
            else:
                # grass checker
                if (row + col) % 2 == 0:
                    baseColor = rgb(170, 215, 81)  # Light grass
                else:
                    baseColor = rgb(162, 209, 73)  # Dark grass
                
                # hover / win flash color
                isFlashing = getattr(app, 'winFlashTimer', 0) > 0
                if app.hoveredCell == (row, col) or isFlashing:
                    cellColor = rgb(191, 225, 125) # Hover / Flash color
                else:
                    cellColor = baseColor
                
                drawRect(l, t, cellW, cellH, fill=cellColor)
                
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
                if app.hoveredCell == (row, col) or isFlashing:
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

def drawBoardBorder(app):
  # draw the board outline (with double-thickness):
  drawRect(app.boardLeft, app.boardTop, app.boardWidth, app.boardHeight,
           fill=None, border='black',
           borderWidth=2*app.cellBorderWidth)

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