from cmu_graphics import *
import random

def onAppStart(app):
    app.width = app.height = 750
    app.stepsPerSecond = 10
    app.rows = 30
    app.cols = 30
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
    app.timer = 0

def restartApp(app):
    app.paused = False
    app.board = [[Cell(row, col) for col in range (app.cols)] for row in range(app.rows)]
    app.score = 0
    app.gameOver = False
    app.firstClick = True
    app.timer = 0

def placeMines(app, startRow, startCol):
    #Safe zone (the clicked cell and its 8 neighbors)
    safeZones = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            safeZones.append((startRow + dr, startCol + dc))

    # Place the mines
    for row in range(app.rows):
        for col in range(app.cols):
            if (row, col) not in safeZones:
                if random.random() < app.prob:
                    app.board[row][col].hasMine = True
    
    #Count neighbors
    for row in range(app.rows):
        for col in range(app.cols):
            if not app.board[row][col].hasMine:
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = row + dr, col + dc
                        if (0 <= nr < app.rows and 0 <= nc < app.cols and 
                            app.board[nr][nc].hasMine):
                            count += 1
                app.board[row][col].adjacentMines = count

class Cell:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.hasMine = False
        self.revealed = False
        self.flagged = False
        self.adjacentMines = 0
        
def getCell(app, x, y):
    if (app.boardLeft <= x <= app.boardLeft + app.boardWidth and
        app.boardTop <= y <= app.boardTop + app.boardHeight):
        col = int((x - app.boardLeft) / (app.boardWidth / app.cols))
        row = int((y - app.boardTop) / (app.boardHeight / app.rows))
        return (row, col)
    return None

def onMousePress(app, mouseX, mouseY, button):
    if app.gameOver: return
    
    coords = getCell(app, mouseX, mouseY)
    if coords is None: return
    row, col = coords
    cell = app.board[row][col]

    # Right Click
    if button == 2:
        if not cell.revealed:
            cell.flagged = not cell.flagged
            
    # Left Click
    elif button == 0:
        if cell.flagged: return 
        
        if app.firstClick:
            placeMines(app, row, col)
            app.firstClick = False

        if cell.hasMine:
            app.gameOver = True
            revealAllMines(app)
        else:
            revealCell(app, row, col)
            checkWin(app)

def revealAllMines(app):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col].hasMine:
                app.board[row][col].revealed = True

def checkWin(app):
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            if not cell.hasMine and not cell.revealed:
                return
    app.gameOver = True
    print("You Win!")

def revealCell(app, r, c): #iterative not recursive bc we want to limit the revealed cells
    if not (0 <= r < app.rows and 0 <= c < app.cols): return
    cell = app.board[r][c]
    if cell.revealed: return
    
    cell.revealed = True
    # Recursive reveal if the cell is empty (0 neighbors)
    if cell.adjacentMines == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                revealCell(app, r + dr, c + dc)

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

def takeStep(app):
    app.timer += 0.1

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill='darkGray') # Background
    drawStatus(app)
    drawBoard(app)
    drawCells(app)
    drawBoardBorder(app)
    drawTimer(app)
    
    if app.gameOver:
        # Semi-transparent overlay
        drawRect(0, 0, app.width, app.height, fill='black', opacity=30)
        drawLabel('GAME OVER', app.width/2, app.height/2, 
                  size=40, bold=True, fill='white', border='black')
        drawLabel('Press any key to restart', app.width/2, app.height/2 + 50, 
                  size=20, fill='white')
    
def drawTimer(app):
    drawOval(app.width-25, 50, 150, 50, fill='lightblue', align='right')
    drawLabel(f'Timer: {pythonRound(app.timer, 2)}', app.width-150, 50,align='left', size=20)


def drawStatus(app):
    drawLabel(f'Score: {app.score}', 50, 50, size=20, align='left')
    drawLabel('Minesweeper', app.width/2, 50, size=30, bold=True)
    
def drawCells(app):
    for row in range(app.rows):
        for col in range(app.cols):
            cell = app.board[row][col]
            l, t = getCellLeftTop(app, row, col)
            w, h = getCellSize(app)
            
            if cell.revealed:
                drawRect(l, t, w, h, fill='white', border='black', borderWidth=0.5)
                if cell.hasMine:
                    drawCircle(l + w/2, t + h/2, w/3, fill='black')
                elif cell.adjacentMines > 0:
                    drawLabel(cell.adjacentMines, l + w/2, t + h/2, size=w*0.8)
            elif cell.flagged:
                drawLabel('🚩', l + w/2, t + h/2, size=w*0.8)

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
             fill=color, border='black',
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

def main():
    runApp()

main()