from cmu_graphics import *
from button import Button
from ui_checks import switchScreen, _isGuarded

#Handles the start screen

def getStartButtons(app):
    cx = app.width / 2
    btnW, btnH = app.width * 0.27, app.height * 0.07
    gap = app.height * 0.08
    startY = app.height * 0.68
    return [
        Button(cx, startY + btnH/2, btnW, btnH, "Play", textSize=24),
        Button(cx, startY + gap + btnH/2, btnW, btnH, "Custom Mode", textSize=24),
        Button(cx, startY + gap*2 + btnH/2, btnW, btnH, "Instructions", textSize=24),
    ]

def start_redrawAll(app):
    skyColor = rgb(68, 191, 244)
    grassColor = rgb(74, 117, 44)
    splitY = app.height * 0.55
    drawRect(0, 0, app.width, splitY, fill=skyColor)
    drawRect(0, splitY, app.width, app.height - splitY, fill=grassColor)
    
    if getattr(app, 'openingImage', None):
        # Image is 688x230. Scale maintaining aspect ratio (max 80% width or 35% height)
        imgScale = min((app.width * 0.8) / 688, (app.height * 0.35) / 230)
        imgW, imgH = 688 * imgScale, 230 * imgScale
        drawImage(app.openingImage, app.width/2, splitY, align='center',
                  width=imgW, height=imgH)
    
    drawLabel("MINESWEEPER", app.width/2, app.height * 0.15, size=60, bold=True, fill='white')
    
    for btn in getStartButtons(app):
        btn.draw()

#Used some ai here to debug the button pressing (some would double press or not register)
def start_onMousePress(app, mouseX, mouseY):
    if _isGuarded(app): return
    buttons = getStartButtons(app)
    if buttons[0].contains(mouseX, mouseY):
        switchScreen(app, 'game')
    elif buttons[1].contains(mouseX, mouseY):
        switchScreen(app, 'custom')
    elif buttons[2].contains(mouseX, mouseY):
        switchScreen(app, 'instructions')

def start_onStep(app):
    app.screenGuard = False
