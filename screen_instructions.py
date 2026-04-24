from cmu_graphics import *
from button import Button
from ui_checks import switchScreen, _isGuarded

#Handles the instructions screen

def getInstructionsBackButton(app):
    btnW, btnH = 80, 40
    return Button(60, 40, btnW, btnH, "Back", textSize=16)

def instructions_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=rgb(74, 117, 44))
    drawLabel("Instructions", app.width/2, app.height * 0.1, size=40, bold=True, fill='white')
    rules = [
        "The Objective",
        "Clear the entire grid without detonating any hidden mines.",
        "You win when every single safe square has been revealed!",
        "",
        "The Controls",
        "Left-Click: Reveal a square. (If it's a mine, it's Game Over)",
        "Right-Click: Plant a flag. Use this to mark squares where you are sure a mine is hiding.",
        "Space: Press space to reset the game",
        "No Guess Mode: The game guarantees the board can be solved without guessing.",
        "",
        "The Numbers",
        "When you reveal an empty square, a number will appear.",
        "This number tells you exactly how many mines are touching that specific square",
        "in all 8 directions (top, bottom, left, right, and diagonals).",
        ""
    ]
    ruleStartY = app.height * 0.2
    lineSpacing = app.height * 0.04
    for i, line in enumerate(rules):
        drawLabel(line, 25, ruleStartY + i * lineSpacing, size=18, fill='white', align='left')
    
    getInstructionsBackButton(app).draw()

def instructions_onMousePress(app, mouseX, mouseY):
    if _isGuarded(app): return
    if getInstructionsBackButton(app).contains(mouseX, mouseY):
        switchScreen(app, 'start')

def instructions_onStep(app):
    app.screenGuard = False
