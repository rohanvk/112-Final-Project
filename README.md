# Minesweeper

A fully-featured Minesweeper clone built with CMU Graphics for the 15-112 Final Project.

## Features

- **Three Difficulty Modes**: Easy (8×10, 10 mines), Medium (14×18, 40 mines), Hard (20×24, 99 mines)
- **Custom Game Mode**: Create your own board with configurable rows, columns, and mine count
- **No-Guess Mode**: Boards are guaranteed to be solvable without guessing using a multi-tier logical solver
- **Auto-Solver**: Watch an AI robot solve the board step-by-step with visual move indicators
- **Full Audio**: Dig sounds, flag sounds, mine explosions, and win/lose music (with mute toggle)
- **Animations**: Cell reveal animations, flag plant/remove physics, mine explosions with confetti, and screen shake
- **Multiple Screens**: Start screen, instructions screen, custom game setup, and the game itself

## How to Play

1. **Left click** to reveal a cell
2. **Right click** to place or remove a flag
3. Numbers show how many mines are adjacent to that cell
4. Clear all non-mine cells to win!

## Controls

| Key / Action | Effect |
|---|---|
| Left Click | Reveal a cell |
| Right Click | Place / remove a flag |
| Space | Restart the current game |
| P | Pause / unpause |

## Project Structure

```text
├── main.py                # App entry point, screen routing
├── config.py              # Game constants and shared configuration
├── game_engine.py         # Centralized game state and core logic orchestration
├── screen_start.py        # Start screen interaction logic
├── screen_instructions.py # Instructions screen interaction logic
├── screen_custom.py       # Custom game setup screen logic
├── screen_game.py         # Game screen input handlers and interaction logic
├── board.py               # Cell class, board generation, mine placement
├── ui.py                  # All drawing functions, menus, game-over screens
├── ui_checks.py           # Reusable UI element click detection
├── button.py              # Reusable Button class for screen UIs
├── animations.py          # Cell, flag, confetti, and explosion animations
├── solver.py              # Solver orchestrator (no-guess verification + auto-solver)
├── solver_utils.py        # Pure logic analysis (Basic, Advanced, Global deductions)
├── images/                # UI images (flags, audio icon, win/lose screens)
└── audio/                 # Sound effects and music
```

## Architecture

### Solver

The solver uses three tiers of logical deduction:

1. **Tier 1 (Basic)**: For each revealed number, if all adjacent mines are found, remaining hidden neighbors are safe. If hidden + flagged equals the number, all hidden are mines.
2. **Tier 2 (Advanced)**: Uses constraint propagation between overlapping numbered cells via BFS to find deductions that basic logic misses.
3. **Global**: Compares total remaining mines against total unknown cells to deduce when all unknowns are mines or all unknowns are safe.

### No-Guess Board Generation

When No-Guess Mode is enabled, the game regenerates the board until the solver can fully clear it from the starting click without any guessing. This guarantees a fair, logic-only experience.

### Screen System

Uses CMU Graphics' `runAppWithScreens` with a transition guard to prevent click events from leaking between screens:
- `start` — Main menu with the Minesweeper opening image
- `instructions` — Rules and explanation of No-Guess Mode
- `custom` — Configure rows, columns, mines, and No-Guess Mode toggle
- `game` — The actual Minesweeper gameplay

## Requirements

- Python 3
- CMU Graphics (`cmu_graphics`)
- Pillow (`PIL`)

## Running

```bash
python main.py
```

## Credits

- Images and audio from the [Google Minesweeper](https://www.google.com/search?q=minesweeper) game
- Built with [CMU Graphics](https://academy.cs.cmu.edu/desktop) for 15-112
