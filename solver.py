#Heavy ai used here, plan/idea was mine
from solver_utils import analyze_tier_1, analyze_tier_2, analyze_global
from board import *
from animations import *

def isBoardSolvableNoGuesses(app, startRow, startCol):
    rows, cols = app.rows, app.cols
    board = app.board
    
    revealed = set()
    known_mines = set()
    known_safe = set([(startRow, startCol)])
    
    # Helper to reveal a cell and propagate 0s
    def reveal(r, c):
        if (r, c) in revealed: return
        revealed.add((r, c))
        if board[r][c].adjacentMines == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if (nr, nc) not in revealed and (nr, nc) not in known_mines:
                            known_safe.add((nr, nc))
                            reveal(nr, nc)
                            
    reveal(startRow, startCol)
    
    total_cells = rows * cols
    
    while True:
        progress = False
        
        if len(known_mines) + len(known_safe) == total_cells:
            return True
            
        # Basic
        actions = analyze_tier_1(board, rows, cols, revealed, known_mines)
        if actions:
            for actType, cell in actions:
                if actType == 'reveal':
                    known_safe.add(cell)
                    reveal(cell[0], cell[1])
                elif actType == 'flag':
                    known_mines.add(cell)
            progress = True
            
        if not progress:
            # Advanced
            actions = analyze_tier_2(board, rows, cols, revealed, known_mines)
            if actions:
                for actType, cell in actions:
                    if actType == 'reveal':
                        known_safe.add(cell)
                        reveal(cell[0], cell[1])
                    elif actType == 'flag':
                        known_mines.add(cell)
                progress = True
                
        if not progress:
            actions = analyze_global(rows, cols, app.numMines, revealed, known_mines)
            if actions:
                for actType, cell in actions:
                    if actType == 'reveal':
                        known_safe.add(cell)
                        reveal(cell[0], cell[1])
                    elif actType == 'flag':
                        known_mines.add(cell)
                progress = True
                
        if not progress:
            return False
            
    return True

def getNextSolverAction(app):
    rows, cols = app.rows, app.cols
    board = app.board
    
    revealed = [(r, c) for r in range(rows) for c in range(cols) if board[r][c].revealed]
    known_mines = set([(r, c) for r in range(rows) for c in range(cols) if board[r][c].flagged])
    
    if not revealed:
        return ('reveal', (rows // 2, cols // 2))

    actions = analyze_tier_1(board, rows, cols, revealed, known_mines)
    if actions: return actions[0]
    
    actions = analyze_tier_2(board, rows, cols, revealed, known_mines)
    if actions: return actions[0]
    
    actions = analyze_global(rows, cols, app.numMines, revealed, known_mines)
    if actions: return actions[0]
    
    return None

def autoSolverLogic(app):
    if getattr(app, 'autoSolve', False):
        if getattr(app, 'autoSolveTimer', 0) <= 0:
            app.autoSolveTimer = 2 # run every 2 steps
            
            action = getNextSolverAction(app)
            if action:
                actType, (r, c) = action
                app.solverTarget = (r, c)
                
                cell = app.board[r][c]
                if actType == 'reveal':
                    if app.firstClick:
                        placeMines(app, r, c)
                        app.firstClick = False
                        app.startTime = time.time() - 1
                        app.timer = 1
                    if not cell.flagged:
                        if cell.hasMine:
                            startGameOver(app, cell, (r, c))
                        else:
                            wonGame(app, (r, c))
                elif actType == 'flag':
                    if not cell.flagged:
                        cell.flagged = True
                        cell.isFlagAnimating = True
                        cell.flagScale = 0.1
                        try:
                            if getattr(app, 'plantSound', None) and not getattr(app, 'muted', False): app.plantSound.play(restart=True)
                        except:
                            pass
            else:
                app.solverTarget = None
                app.autoSolve = False # Stuck or done
        else:
            app.autoSolveTimer -= 1
            