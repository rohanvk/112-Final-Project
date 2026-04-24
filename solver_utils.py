from collections import deque

#basic logic, returns simple logic outcomes
def analyze_tier_1(board, rows, cols, revealed, known_mines):

    actions = []
    active_revealed = [(r, c) for (r, c) in revealed if board[r][c].adjacentMines > 0]
    
    for r, c in active_revealed:
        adj_mines = board[r][c].adjacentMines
        
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    neighbors.append((nr, nc))
                    
        hidden = [n for n in neighbors if n not in revealed and n not in known_mines]
        mines = [n for n in neighbors if n in known_mines]
        
        if len(mines) == adj_mines and len(hidden) > 0:
            for n in hidden:
                actions.append(('reveal', n))
                
        elif len(mines) + len(hidden) == adj_mines and len(hidden) > 0:
            for n in hidden:
                actions.append(('flag', n))
                
    return list(set(actions))

#advanced logic, uses bfs to find solutions
def analyze_tier_2(board, rows, cols, revealed, known_mines):

    actions = []
    active_revealed = [(r, c) for (r, c) in revealed if board[r][c].adjacentMines > 0]
    
    frontier_cells = set()
    constraints = {}
    
    for r, c in active_revealed:
        adj_mines = board[r][c].adjacentMines
        mines_count = 0
        hidden_neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if (nr, nc) in known_mines:
                        mines_count += 1
                    elif (nr, nc) not in revealed:
                        hidden_neighbors.append((nr, nc))
                        
        if len(hidden_neighbors) > 0:
            constraints[(r, c)] = {
                'target': adj_mines - mines_count,
                'cells': hidden_neighbors
            }
            for hn in hidden_neighbors:
                frontier_cells.add(hn)
                
    if not frontier_cells:
        return actions
        
    adj_frontier = {cell: set() for cell in frontier_cells}
    for const in constraints.values():
        cells = const['cells']
        for i in range(len(cells)):
            for j in range(i+1, len(cells)):
                adj_frontier[cells[i]].add(cells[j])
                adj_frontier[cells[j]].add(cells[i])
                
    components = []
    visited = set()
    for cell in frontier_cells:
        if cell not in visited:
            comp = set()
            q = deque([cell])
            visited.add(cell)
            while q:
                curr = q.popleft()
                comp.add(curr)
                for neighbor in adj_frontier[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
            components.append(comp)
            
    for comp in components:
        comp_list = list(comp)
        comp_constraints = []
        for (r,c), const in constraints.items():
            if any(cell in comp for cell in const['cells']):
                comp_constraints.append(const)
                
        valid_configs = []
        queue = deque([ {} ])
        iterations = 0
        
        while queue:
            iterations += 1
            if iterations > 2500:
                valid_configs = []
                break
            hypothesis = queue.popleft()
            
            is_consistent = True
            for const in comp_constraints:
                target = const['target']
                cells = const['cells']
                
                assigned_mines = 0
                unassigned = 0
                
                for cell in cells:
                    if cell in hypothesis:
                        if hypothesis[cell]:
                            assigned_mines += 1
                    else:
                        unassigned += 1
                if assigned_mines > target or (assigned_mines + unassigned) < target:
                    is_consistent = False
                    break
            
            if not is_consistent:
                continue
                
            if len(hypothesis) == len(comp_list):
                valid_configs.append(hypothesis)
                continue
                
            next_cell = None
            for cell in comp_list:
                if cell not in hypothesis:
                    next_cell = cell
                    break
            if next_cell:
                h_mine = hypothesis.copy()
                h_mine[next_cell] = True
                queue.append(h_mine)
                h_safe = hypothesis.copy()
                h_safe[next_cell] = False
                queue.append(h_safe)
                
        if not valid_configs:
            continue
            
        for cell in comp_list:
            is_mine_all = True
            is_safe_all = True
            for config in valid_configs:
                if config[cell]:
                    is_safe_all = False
                else:
                    is_mine_all = False
            
            if is_mine_all:
                actions.append(('flag', cell))
            if is_safe_all:
                actions.append(('reveal', cell))
                
    return list(set(actions))

#depending on remaining mines, decides whether it is possible to solve board 
def analyze_global(rows, cols, numMines, revealed, known_mines):
    actions = []
    total_cells = rows * cols
    unknown_cells = total_cells - len(revealed) - len(known_mines)
    remaining_mines = numMines - len(known_mines)
    
    if remaining_mines == 0 and unknown_cells > 0:
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in revealed and (r, c) not in known_mines:
                    actions.append(('reveal', (r, c)))
    elif unknown_cells == remaining_mines and unknown_cells > 0:
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in revealed and (r, c) not in known_mines:
                    actions.append(('flag', (r, c)))
                    
    return actions
