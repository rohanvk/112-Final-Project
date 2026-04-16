from cmu_graphics import *
from PIL import Image as PILImage
import time #need because otherwise timer tracks framerate
from board import *
from ui import *
from solver import *

def onAppStart(app):
    app.width = app.height = 750
    app.stepsPerSecond = 30
    app.rows = 20
    app.cols = 20
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

def restartApp(app):
    app.paused = False
    app.board = [[Cell(row, col) for col in range (app.cols)] for row in range(app.rows)]
    app.score = 0
    app.gameOver = False
    app.firstClick = True
    app.timer = 1
    app.startTime = time.time()

def onMouseMove(app, mouseX, mouseY):
    if app.gameOver:
        app.hoveredCell = None
        return
        
    coords = getCell(app, mouseX, mouseY)
    
    if app.hoveredCell != coords:
        app.hoveredCell = coords

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
    app.timer = int(time.time() - app.startTime)

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

def main():
    runApp()

main()