from collections import deque

#AI helped heavily with making sure these functions were efficient and bug free
#Core ideas were mine, implementations were more AI

#basic logic, returns simple logic outcomes
def analyze_tier_1(board, rows, cols, revealed, known_mines):

    actions = []
    active_revealed = [(r, c) for (r, c) in revealed if board[r][c].adjacentMines > 0]
    
    #Check neighbors for each revealed square
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
        
        #Mines = num then open others
        if len(mines) == adj_mines and len(hidden) > 0:
            for n in hidden:
                actions.append(('reveal', n))
        
        #otherwise flag it if it must have a mine
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
    
    #for each opened cell, look at groups
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

        #constraints are closed cells and number of mines      
        if len(hidden_neighbors) > 0:
            constraints[(r, c)] = {
                'target': adj_mines - mines_count,
                'cells': hidden_neighbors
            }
            for hn in hidden_neighbors:
                frontier_cells.add(hn)

    #once we checked everything open or flag cells          
    if not frontier_cells:
        return actions
    
    #combine sets of groups
    adj_frontier = {cell: set() for cell in frontier_cells}
    for const in constraints.values():
        cells = const['cells']
        for i in range(len(cells)):
            for j in range(i+1, len(cells)):
                adj_frontier[cells[i]].add(cells[j])
                adj_frontier[cells[j]].add(cells[i])

    #used deque for efficiency, can add/remove from either end          
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
                #go through each of the neighbors of the cell and add them
                for neighbor in adj_frontier[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
            components.append(comp)
    
    #go through each possibility and see if they fit the constraints
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
            #only look for frontiers a max of 2500 times, prevents too much time wasted on a board
            if iterations > 2500:
                valid_configs = []
                break
            hypothesis = queue.popleft()
            
            #check the possibilty if it fits constraints
            is_consistent = True
            for const in comp_constraints:
                target = const['target']
                cells = const['cells']
                
                assigned_mines = 0
                unassigned = 0
                
                #assign mines accordingly
                for cell in cells:
                    if cell in hypothesis:
                        if hypothesis[cell]:
                            assigned_mines += 1
                    else:
                        unassigned += 1
                if assigned_mines > target or (assigned_mines + unassigned) < target:
                    is_consistent = False
                    break
            
            #skip if it doesnt work
            if not is_consistent:
                continue

            #if it does add it  
            if len(hypothesis) == len(comp_list):
                valid_configs.append(hypothesis)
                continue
            
            #Get the next cell
            next_cell = None
            for cell in comp_list:
                if cell not in hypothesis:
                    next_cell = cell
                    break
            #Assume the next cell is a mine and add it, assume its empty and add it
            if next_cell:
                h_mine = hypothesis.copy()
                h_mine[next_cell] = True
                queue.append(h_mine)
                h_safe = hypothesis.copy()
                h_safe[next_cell] = False
                queue.append(h_safe)
        
        #no ways to solve the board       
        if not valid_configs:
            continue

        #if a cell is a mine in all possibilities or safe in all possibilities, act on it   
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
    
    #if theres no mines, open everything
    if remaining_mines == 0 and unknown_cells > 0:
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in revealed and (r, c) not in known_mines:
                    actions.append(('reveal', (r, c)))
                    
    #if everything is a mine, flag it all
    elif unknown_cells == remaining_mines and unknown_cells > 0:
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in revealed and (r, c) not in known_mines:
                    actions.append(('flag', (r, c)))
                    
    return actions
