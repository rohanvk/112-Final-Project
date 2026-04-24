from cmu_graphics import *
from ui import *
import random



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

#animation on mine open
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

    # get cell center and spawn confetti
    l, t = getCellLeftTop(app, row, col)
    w, h = getCellSize(app)
    cx, cy = l + w/2, t + h/2
    spawnLoseConfetti(app, cx, cy, mineBgColor)
    
    # play random mine sound on explode
    if app.mineSounds:
        mineSound = random.choice(app.mineSounds)
        if mineSound is not None and not getattr(app, 'muted', False):
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

#flag animations (used light ai for outlining)
def stepFlagAnimations(cell):
    if cell.isFlagAnimating:
        cell.flagScale += 0.4 
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

#faster and no flutter compared to lose confetti (als0 no fade out)
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

# used some ai to create this
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
        # Flutter effect (ai)
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

#make the confetti!
def drawConfetti(app):
    for p in getattr(app, 'confetti', []):
        # Only draw it if it's on the screen and visible
        if p['y'] < app.height and p.get('opacity', 100) > 0:
            drawRect(p['x'], p['y'], p['size'], p['size'], 
                     fill=p['color'], align='center', opacity=p.get('opacity', 100))
