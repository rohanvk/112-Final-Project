from cmu_graphics import *
from board import *

def drawTimer(app):
    drawOval(app.width-25, 50, 150, 50, fill='lightblue', align='right')
    drawLabel(f'Timer: {pythonRound(app.timer, 1)}', app.width-150, 50,align='left', size=20)

def drawStatus(app):
    drawLabel(f'Score: {app.score}', 50, 50, size=20, align='left')
    drawLabel('Minesweeper', app.width/2, 50, size=30, bold=True)
    
def drawCells(app):
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            l, t = getCellLeftTop(app, row, col)
            w, h = getCellSize(app)
            
            cx = l + w/2
            cy = t + h/2
            
            if cell.revealed:
                if cell.hasMine:
                    # mines
                    # get random index for mines
                    colorIndex = (row * 11 + col * 17) % 8 + 1
                    mineBgColor, mineCircleColor = app.numberColors[colorIndex]
                    
                    # background = light color
                    drawRect(l, t, w, h, fill=mineBgColor)
                    
                    # center = dark color
                    radius = min(w, h) * 0.35
                    drawCircle(cx, cy, radius, fill=mineCircleColor)
                else:
                    # dirt checker
                    if (row + col) % 2 == 0:
                        dirtColor = rgb(229, 194, 159)
                    else:
                        dirtColor = rgb(215, 184, 153)
                    
                    drawRect(l, t, w, h, fill=dirtColor)
                    
                    if cell.adjacentMines > 0:
                        # Get color for num
                        numColor = app.textColors[cell.adjacentMines]
                        drawLabel(cell.adjacentMines, cx, cy, size=w*0.8, bold=True, fill=numColor, font='arial')
            else:
                # grass checker
                if (row + col) % 2 == 0:
                    baseColor = rgb(170, 215, 81)  # Light grass
                else:
                    baseColor = rgb(162, 209, 73)  # Dark grass
                
                # hover color
                if app.hoveredCell == (row, col):
                    cellColor = rgb(191, 225, 125) # Hover effect
                else:
                    cellColor = baseColor
                
                drawRect(l, t, w, h, fill=cellColor)
                
                if cell.flagged:
                    drawImage(app.flagImage, cx, cy, align='center',width=w*0.8, height=h*0.8)

    # Loop 2 to draw an edge between the borders of the grass and opened cells, ai assisted
    edgeColor = rgb(135, 175, 58)
    edgeThickness = 2
    
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            
            if cell.revealed:
                l, t = getCellLeftTop(app, row, col)
                w, h = getCellSize(app)
                
                # if top
                if row > 0 and not app.board[row-1][col].revealed:
                    drawLine(l, t, l + w, t, fill=edgeColor, lineWidth=edgeThickness)
                
                # if bottom
                if row < app.rows - 1 and not app.board[row+1][col].revealed:
                    drawLine(l, t + h, l + w, t + h, fill=edgeColor, lineWidth=edgeThickness)
                
                # if left
                if col > 0 and not app.board[row][col-1].revealed:
                    drawLine(l, t, l, t + h, fill=edgeColor, lineWidth=edgeThickness)
                
                # if right
                if col < app.cols - 1 and not app.board[row][col+1].revealed:
                    drawLine(l + w, t, l + w, t + h, fill=edgeColor, lineWidth=edgeThickness)

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