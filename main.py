import sys
import os

# Redirect stdout and stderr to devnull if they are None to prevent crashes in unwindowed exes
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

#For all citations of AI, Gemini Pro 3.1 was used (Claude Opus 4.6 (thinking and planning) was used for finding bugs)
#All images and audio from the Google Minesweeper game unless otherwise cited

#Dev commands: p to pause, w to win state, e to lose state, space to reset current board

#Feature list:
'''
Three Difficulties: Pre-configured board sizes and mine counts for Easy (8×10, 10 mines), Medium (14×18, 40 mines), and Hard (20×24, 99 mines).
Custom Game Mode: configure board size, mine counts, if the no guess algorithm should be used.
No-Guess Mode: guarantees the board can be solved purely through logic without any blind guessing. The game automatically regenerates the board.

3 tier solver: A built-in solver engine that powers No-Guess mode using:
    Basic: Standard adjacent mine/flag deductions.
    Advanced: Constraint propagation using BFS between overlapping numbered cells.
    Global: Deductions based on comparing total remaining mines to total unknown cells.
Autosolver: renders algorithm with full graphics and audio.
Audio: Sound effects for digging, planting flags, and mine explosions, plus background music for win/lose states. Includes mute.
Score: Keeps best time for every map, including custom boards

Animations:
    Cell reveal animations (with physics)
    Cell edge outlines dynamically updated
    Physics-based flag planting and removal
    Mine explosions featuring confetti particles
    Screen shake effects
    ROUNDED CORNER RECTANGLES
    Support for any size screen

Multiple Screens: includes guards to prevent early switching or unexpected behavior
    Start Screen: Main menu with opening imagery.
    Instructions Screen: Rules and an explanation of the No-Guess mechanics.
    Custom Setup Screen: Configuration for custom games.
    Game Screen: The main Minesweeper interface.

Controls: left-click (reveal), right-click (flag), spacebar (restart), and 'P' (pause/unpause).'''

from cmu_graphics import *
from PIL import Image as PILImage #image optimization
import time #need because otherwise timer tracks framerate

from board import *
from config import DIFFICULTIES, NUMBER_COLORS, TEXT_COLORS
from ui import *
from ui_checks import *
from game_engine import *
from solver import *
from button import Button
from animations import *
from screen_start import *
from screen_instructions import *
from screen_custom import *
from screen_game import *

def onAppStart(app):
    app.isLoaded = False
    app.width = app.height = 750
    app.stepsPerSecond = 20
    app.rows = 14
    app.cols = 18
    app.boardLeft = 0
    app.boardTop = 90
    app.boardWidth = app.width
    app.boardHeight = app.height - 90
    app.cellBorderWidth = 0.5
    app.paused = False
    app.board = [[Cell(row, col) for col in range (app.cols)] for row in range(app.rows)]

    app.score = 0
    app.gameOver = False
    app.isWin = False
    app.forcedWin = False
    app.numMines = 40
    app.firstClick = True
    app.startTime = time.time()
    app.timer = 0
    app.hoveredCell = None

    app.confetti = []
    app.bestScores = {"Easy": [], "Medium": [], "Hard": []}
    app.winFlashTimer = 0
    app.isDropdownOpen = False
    app.menuHoveredItem = None
    app.currentDifficulty = "Medium"
    app.menuShiftX = 0       
    app.noGuessMode = True
    app.checkmarkIndentX = 30
    app.endflag = False
    app.winnerMusicTimer = 0
    app.muted = False
    app.screenGuard = False
    app.customRows = 14
    app.customCols = 18
    app.customMines = 40
    app.customNoGuess = True
    app.customConfigured = False

    # Audio
    try:
        rawAudio = PILImage.open(get_path('images/Audio.png'))
        resizedAudio = rawAudio.resize((30, 30))
        app.audioImage = CMUImage(resizedAudio)
    except:
        app.audioImage = None

    app.bigDigSound = Sound(get_path('audio/game_audio BIG_DIG.mp3'))
    app.mineSounds = [s for s in [Sound(get_path(f'audio/game_audio MINE_{i}.mp3')) for i in range(1, 6)] if s is not None]
    app.digSounds = [s for s in [Sound(get_path(f'audio/game_audio DIG_REVEAL_{i}.mp3')) for i in range(1, 9)] if s is not None]
    app.soundsPlayedThisStep = 0
    app.plantSound = Sound(get_path('audio/game_audio PLANT_FLAG.mp3'))
    app.unplantSound = Sound(get_path('audio/game_audio UNPLANT_FLAG.mp3'))
    app.loseMusic = Sound(get_path('audio/music_audio LOSE_MUSIC.mp3'))
    app.winHarp = Sound(get_path('audio/music_audio WIN_WATER_HARP.mp3'))
    app.winMusic = Sound(get_path('audio/music_audio WINNER_MUSIC.mp3'))

    app.difficulties = DIFFICULTIES
    
    # Menu location and size
    app.menuX = 20
    app.menuY = 25
    app.menuW = 100
    app.menuH = 40

    app.numberColors = NUMBER_COLORS
    app.textColors = TEXT_COLORS

    #image optimization (ai helped with this)
    imageWidth = 60
    imageHeight = 60
        
    rawFlag = PILImage.open(get_path('images/flag.png'))
    resizedFlag = rawFlag.resize((imageWidth, imageHeight))
    app.flagImage = CMUImage(resizedFlag)
    rawArrow = PILImage.open(get_path('images/downArrow.png'))
    app.downArrow = CMUImage(rawArrow)
    rawCheck = PILImage.open(get_path('images/checkmark.png'))
    app.checkmark = CMUImage(rawCheck)
    rawTimer = PILImage.open(get_path('images/timerimage.png'))
    resizedTimer = rawTimer.resize((44, 54))
    app.timerimage = CMUImage(resizedTimer)
    rawTry = PILImage.open(get_path('images/Try again.png'))
    app.tryagain = CMUImage(rawTry)
    rawWin = PILImage.open(get_path('images/Win screen.png'))
    app.winimage = CMUImage(rawWin)
    rawLose = PILImage.open(get_path('images/Lose screen.png'))
    app.loseimage = CMUImage(rawLose)
    rawOpening = PILImage.open(get_path('images/Minesweeper opening page.png'))
    app.openingImage = CMUImage(rawOpening)
    app.isLoaded = True

def main():
    runAppWithScreens(initialScreen='start')



#Ignore this function, it is for the EXE version of my code
import sys
import os

def get_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller EXE """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

main()