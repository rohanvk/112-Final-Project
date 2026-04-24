from cmu_graphics import *
from ui import *
import random

def lossAnimation(app):
    stillExploding = False
    for r in range(app.rows):
        for c in range(app.cols):
            cell = app.board[r][c]
            if (cell.hasMine or cell.flagged) and cell.waveDelay > -1:
                stillExploding = True
                cell.waveDelay -= 1
                if cell.waveDelay <= 0:
                    if cell.flagged:
                        popFlags(cell)
                    if cell.hasMine:
                        openMines(app, cell, r, c)
    if not stillExploding:
        if not app.endflag:
            try:
                if getattr(app, 'loseMusic', None): app.loseMusic.play(restart=True)
            except:
                pass
        app.endflag = True

def triggerWin(app):
    if app.firstClick:
        from board import placeMines
        placeMines(app, 0, 0)
        app.firstClick = False
    
    app.gameOver = True
    app.isWin = True
    app.endflag = True
    app.forcedWin = True
    app.winFlashTimer = 10
    
    # Audio
    try:
        if getattr(app, 'loseMusic', None): app.loseMusic.pause()
        if getattr(app, 'winMusic', None): app.winMusic.pause()
    except:
        pass

    try:
        if getattr(app, 'winHarp', None): app.winHarp.play()
    except:
        pass
    app.winnerMusicTimer = 80 # Play win music after harp (~4 seconds)

    # Save score
    if app.currentDifficulty in app.bestScores:
        app.bestScores[app.currentDifficulty].append(app.timer)
        app.bestScores[app.currentDifficulty].sort()
    # Pop all flags and generate confetti
    app.confetti = []
    for r in range(app.rows):
        for c in range(app.cols):
            checkCell = app.board[r][c]
            if checkCell.flagged:
                popFlags(checkCell)
    spawnWinConfetti(app)



def wonGame(app, coords):
    row, col = coords
    cell = app.board[row][col]
    revealedCount = revealCell(app, row,col)
    
    # Play reveal sounds
    if revealedCount > 10:
        if app.bigDigSound is not None:
            app.bigDigSound.play(restart=True)
    elif revealedCount > 0:
        adj = cell.adjacentMines
        if 1 <= adj <= 8:
            if app.digSounds[adj-1] is not None:
                app.digSounds[adj-1].play(restart=True)
        else:
            if app.digSounds[0] is not None:
                app.digSounds[0].play(restart=True)

    if revealedCount > 10:
        app.shakeTimer = 5 # shake screen
    
    if checkWin(app) or app.forcedWin:
        triggerWin(app)

def popFlags(cell):
    cell.flagged = False
    cell.isFlagDespawning = True
    cell.flagDespawnScale = 1.0
    cell.flagDespawnOffsetX = 0
    cell.flagDespawnOffsetY = 0
    cell.flagDespawnDy = random.uniform(-18, -10)
    cell.flagDespawnDx = random.uniform(-10, 10)

#difference between these two functions is that the top is more aggresive and also removes the flags entirely
def removeFlag(cell):
    cell.isFlagDespawning = True
    cell.flagDespawnScale = 1.0
    cell.flagDespawnOffsetX = 0
    cell.flagDespawnOffsetY = 0
    #pop up and then out
    cell.flagDespawnDy = random.randint(-12, -8) 
    cell.flagDespawnDx = random.randint(-4, 4)

def openMines(app, cell, row, col):
    cell.revealed = True
    cell.isAnimating = True
    cell.animScale = 1.0
    cell.animOffsetX = 0
    cell.animOffsetY = 0
    cell.animDx = random.choice([-1, 1]) * random.randint(3, 8)
    cell.animDy = random.choice([-1, 1]) * random.randint(3, 8)

    # get unique color
    colorIndex = (row * 11 + col * 17) % 8 + 1
    mineBgColor, _ = app.numberColors[colorIndex]
    # get cell center
    l, t = getCellLeftTop(app, row, col)
    w, h = getCellSize(app)
    cx, cy = l + w/2, t + h/2
    spawnLoseConfetti(app, cx, cy, mineBgColor)
    
    # Play random mine sound
    if app.mineSounds:
        mineSound = random.choice(app.mineSounds)
        if mineSound is not None:
            mineSound.play(restart=True)

def stepCellAnimations(cell):
    # if cell animating, change animation
    if cell.isAnimating:
        cell.animScale -= 0.11     # Shrink by 10% every frame
        cell.animOffsetX += cell.animDx # Move X
        cell.animOffsetY += cell.animDy # Move Y
        
        # stop animation
        if cell.animScale <= 0:
            cell.animScale = 0
            cell.isAnimating = False

def stepFlagAnimations(cell):
    if cell.isFlagAnimating:
        cell.flagScale += 0.4  # Increase size by 20% per frame
        if cell.flagScale >= 1.0:
            cell.flagScale = 1.0
            cell.isFlagAnimating = False

def stepFlagDespawn(cell):
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

def spawnWinConfetti(app):
    confettiColors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    for i in range(150):
        app.confetti.append({
            'x': random.randint(0, app.width),
            'y': random.randint(-300, -50),
            'dx': random.randint(-6, 6),
            'dy': random.randint(2, 12),
            'size': random.randint(6, 12),
            'color': random.choice(confettiColors),
            'age': 0,
            'opacity': 100
        })

def spawnLoseConfetti(app, cx, cy, mineBgColor):
    if not hasattr(app, 'confetti'): app.confetti = [] # make sure we have app.confetti
    # add 8 particles for loss
    for _ in range(8):
        app.confetti.append({
            'x': cx,
            'y': cy,
            # Go up
            'dy': random.uniform(-4, -3), 
            # Sideways
            'dx': random.uniform(-5, 5),    
            'size': random.randint(9, 10),
            # Use unique colors
            'color': mineBgColor,
            'age': 0,
            'opacity': 100
        })

def stepConfetti(app):
    for p in getattr(app, 'confetti', []): #used ai for this part to get confetti during end
        p['dy'] += 0.2              # Gravity
        # Flutter effect
        if p['dx'] > 0: p['dx'] -= 0.05
        elif p['dx'] < 0: p['dx'] += 0.05
        
        # Move across screen
        p['x'] += p['dx']
        p['y'] += p['dy']

        # fade out after 40 frames (2 seconds)
        p['age'] = p.get('age', 0) + 1
        if p['age'] > 40:
            p['opacity'] = max(0, p.get('opacity', 100) - 5)

    # Remove if faded
    app.confetti = [p for p in app.confetti if p.get('opacity', 100) > 0]

def drawConfetti(app):
    for p in getattr(app, 'confetti', []):
        # Only draw it if it's on the screen and visible
        if p['y'] < app.height and p.get('opacity', 100) > 0:
            drawRect(p['x'], p['y'], p['size'], p['size'], 
                     fill=p['color'], align='center', opacity=p.get('opacity', 100))
