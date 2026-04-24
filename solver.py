#Heavy ai used here, plan/idea was mine
from solver_utils import analyze_tier_1, analyze_tier_2, analyze_global
from board import *

#This function is for the hidden solver that runs when no guess mode is active
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
                        #recursively opens cells
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
        
        #if we can't do anything, figure out if we are done with the board
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

        #If we can't make progress, give up on the board    
        if not progress:
            return False
            
    return True

#This function is for the visible solver that runs when the autosolve button is pressed
def getNextSolverAction(app):
    rows, cols = app.rows, app.cols
    board = app.board

    #gets the current board state
    revealed = [(r, c) for r in range(rows) for c in range(cols) if board[r][c].revealed]
    known_mines = set([(r, c) for r in range(rows) for c in range(cols) if board[r][c].flagged])
    
    #opens the middle cell if there's nothing open
    if not revealed:
        return ('reveal', (rows // 2, cols // 2))

    #passes up the results of the solver logic one step at a time

    actions = analyze_tier_1(board, rows, cols, revealed, known_mines)
    if actions: return actions[0]
    
    actions = analyze_tier_2(board, rows, cols, revealed, known_mines)
    if actions: return actions[0]
    
    actions = analyze_global(rows, cols, app.numMines, revealed, known_mines)
    if actions: return actions[0]
    
    return None


            