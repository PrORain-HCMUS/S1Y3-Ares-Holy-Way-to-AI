import Search
from Sokoban import Warehouse

def my_team():
    return [
        (22120108, 'Lê Đại Hòa'),
        (22120455, 'Nguyễn Tường Bách Hỷ'),
        (22120459, 'Liêu Hải Lưu Danh'),
        (22120461, 'Lê Hoàng Vũ')
    ]

class SokobanPuzzle(Search.Problem):
    def __init__(self, warehouse,taboocells = None):
        assert isinstance(warehouse,Warehouse)
        self.warehouse =warehouse
        self.initial = self.warehouse_to_state(warehouse)
        if taboocells:
            self.taboocells = taboocells
        else:
            self.taboocells = find_taboo_cells(warehouse)

    def warehouse_to_state(self,warehouse: Warehouse) -> list:
        state = []
        state.append(warehouse.worker)
        state.append(tuple(warehouse.boxes))
        return tuple(state)

    def state_to_warehouse(self,state: tuple) -> Warehouse:
        return self.warehouse.copy(state[0],state[1])

    
    def goal_test(self, state:tuple) -> bool:
        return set(state[1])==set(self.warehouse.targets)

    def actions(self, state:tuple) -> list:
        wh = self.state_to_warehouse(state)
        L = []
        
        wh = self.warehouse.copy(state[0],state[1])

        if  self.is_move_legal(wh,'u'):
            L.append('u')
        if  self.is_move_legal(wh,'d'):
            L.append('d')
        if  self.is_move_legal(wh,'l'):
            L.append('l')
        if  self.is_move_legal(wh,'r'):
            L.append('r')
        return L


    def is_move_legal(self, warehouse : Warehouse, move : str) -> bool:
        deltaDir = direction(move)
        attemptCoor = move_towards(warehouse.worker,deltaDir)

        if(is_coordinate_wall(warehouse,attemptCoor)):
            return False
        elif(is_coordinate_box(warehouse,attemptCoor)):
            if(is_coordinate_wall(warehouse,move_towards(attemptCoor,deltaDir))):
                return False
            elif(is_coordinate_box(warehouse,move_towards(attemptCoor,deltaDir))):
                return False
            elif( move_towards(attemptCoor,deltaDir) in self.taboocells ):
                return False

        return True


    def result(self, state : tuple, action : str) -> tuple:
        wh = self.state_to_warehouse(state)

        deltaDir = direction(action)
        attemptCoor = move_towards(wh.worker,deltaDir)

        if(is_coordinate_box(wh,attemptCoor)):
            wh.boxes = list(wh.boxes)
            for i,boxCor in enumerate(wh.boxes):
                if(boxCor == attemptCoor ):
                    wh.boxes.pop(i)
                    wh.boxes.insert(i,move_towards(attemptCoor,deltaDir))
                    break

        wh.worker = attemptCoor
        return self.warehouse_to_state(wh)
    
    def path_cost(self, c, state1, action, state2):
        wh = self.state_to_warehouse(state1)

        deltaDir = direction(action)
        attemptCoor = move_towards(wh.worker,deltaDir)
        move_cost = 1
        box_weight = 0
        if(is_coordinate_box(wh,attemptCoor)):
                for i,boxCor in enumerate(wh.boxes):
                    if ( boxCor == attemptCoor ):
                        box_weight = self.warehouse.weights[i]
                        break

        return c + move_cost + box_weight


    def get_seq_from_goalnode(self, goal_node):
        path = goal_node.path()
        return [seq.action for seq in path if seq.action]

    def h(self, node):
        if(isinstance(node,Search.Node)):
            h_box = 0
            h_worker = 0
            move_cost = 1
            min_worker_distance = None
            for i,boxCor in enumerate(node.state[1]):
                worker_distance = find_manhattan(boxCor,node.state[0])
                if min_worker_distance == None or worker_distance < min_worker_distance:
                    min_worker_distance = worker_distance
                min_box_distance = None
                for targetCor in self.warehouse.targets:
                    box_distance = find_manhattan(boxCor,targetCor) * (self.warehouse.weights[i] + move_cost)
                    if min_box_distance == None or box_distance < min_box_distance:
                        min_box_distance = box_distance
                h_box+= min_box_distance
            h_worker = min_worker_distance

            return h_worker + h_box -move_cost

def check_elem_action_seq(warehouse: Warehouse, action_seq):
    for seq in action_seq:

        deltaDir = direction(seq)
        attemptCoordinate = move_towards(warehouse.worker, deltaDir)
        
        if is_coordinate_wall(warehouse, attemptCoordinate):
            return 'Impossible'
        elif is_coordinate_box(warehouse, attemptCoordinate):
            move_toward_coordinate = move_towards(attemptCoordinate, deltaDir)
            if is_coordinate_wall(warehouse, move_toward_coordinate):
                return 'Impossible'
            elif is_coordinate_box(warehouse, move_toward_coordinate):
                return 'Impossible'
            else:
                for index, boxCor in enumerate(warehouse.boxes):
                    if boxCor == attemptCoordinate:
                        warehouse.boxes.pop(index)
                        warehouse.boxes.insert(index, move_toward_coordinate)
                        break
        
        warehouse.worker = attemptCoordinate

    return str(warehouse)

def direction (dirInText : str) -> tuple:
    dir = None
    if(dirInText == "l"):
        dir = (-1,0)
    elif(dirInText == "r"):
        dir = (1,0)
    elif(dirInText == "u"):
        dir = (0,-1)
    elif(dirInText == "d"):
        dir = (0,1)
    assert dir != None
    return dir

def is_coordinate_wall(warehouse : Warehouse,coordinate : tuple) -> bool:
    if(len(coordinate) != 2):
        raise ValueError("Coordinate Should Have two values.")
    if(coordinate in warehouse.walls):
        return True
    return False

def is_coordinate_box(warehouse : Warehouse,coordinate : tuple) -> bool:
    if(len(coordinate) != 2):
        raise ValueError("Coordinate Should Have two values.")
    if(coordinate in warehouse.boxes):
        return True
    return False


def find_corner_cells(warehouse: Warehouse) -> list:
    corners = []
    for y in range(warehouse.nrows):
        for x in range(warehouse.ncols):
            if( not (x,y) in warehouse.walls and not (x,y) in warehouse.targets):
                if( ((x-1,y) in warehouse.walls and (x,y-1) in warehouse.walls) or
                    ((x-1,y) in warehouse.walls and (x,y+1) in warehouse.walls) or
                    ((x+1,y) in warehouse.walls and (x,y-1) in warehouse.walls) or
                    ((x+1,y) in warehouse.walls and (x,y+1) in warehouse.walls)
                ):
                    corners.append((x,y))
    return corners

def find_taboo_cells(warehouse: Warehouse) -> list:
    corners = find_corner_cells(warehouse)
    taboos = []
    for x,y in corners:
        for (dx,dy) in [(1,0),(-1,0),(0,1),(0,-1)]:
            checking_cell = (x + dx,y + dy)
            if dy == 0:
                if( checking_cell in corners or checking_cell in warehouse.walls or checking_cell in warehouse.targets):
                    continue
                checking_cell = move_towards(checking_cell, (dx,dy))

                while(not checking_cell in corners  ):
                    if(checking_cell in warehouse.targets or checking_cell in warehouse.walls or checking_cell[0] < 0  or checking_cell[0] > warehouse.ncols - 1):
                        break
                    checking_cell = move_towards(checking_cell, (dx,dy))

                if(checking_cell in warehouse.targets or checking_cell in warehouse.walls or checking_cell[0] < 0  or checking_cell[0] > warehouse.ncols - 1):
                    continue

                t = []
                is_set_taboo = True
                checking_cell = move_towards(checking_cell, (-dx,-dy))

                while(checking_cell != (x,y) ):
                    t.append((checking_cell))
                    checking_cell = move_towards(checking_cell, (-dx,-dy))

                for potential_taboo in t :
                    if not ((potential_taboo[0], potential_taboo[1]-1) in warehouse.walls) :
                        is_set_taboo = False
                        break

                if(not is_set_taboo):
                    is_set_taboo = True
                    for potential_taboo in t :
                        if not ((potential_taboo[0], potential_taboo[1]+1) in warehouse.walls) :
                            is_set_taboo = False
                            break

                if(not is_set_taboo):
                    t = []
                
                taboos = taboos + t

            if dx == 0:
                if( checking_cell in corners or checking_cell in warehouse.walls or checking_cell in warehouse.targets):
                    continue
                checking_cell = move_towards(checking_cell, (dx,dy))

                while(not checking_cell in corners  ):
                    if(checking_cell in warehouse.targets or checking_cell in warehouse.walls or checking_cell[1] < 0  or checking_cell[1] > warehouse.nrows - 1):
                        break
                    checking_cell = move_towards(checking_cell, (dx,dy))

                if(checking_cell in warehouse.targets or checking_cell in warehouse.walls or checking_cell[1] < 0  or checking_cell[1] > warehouse.nrows - 1):
                    continue

                t = []
                is_set_taboo = True
                checking_cell = move_towards(checking_cell, (-dx,-dy))

                while(checking_cell != (x,y) ):
                    t.append((checking_cell))
                    checking_cell = move_towards(checking_cell, (-dx,-dy))

                for potential_taboo in t :
                    if not ((potential_taboo[0]-1, potential_taboo[1]) in warehouse.walls) :
                        is_set_taboo = False
                        break

                if(not is_set_taboo):
                    is_set_taboo = True
                    for potential_taboo in t :
                        if not ((potential_taboo[0]+1, potential_taboo[1]) in warehouse.walls) :
                            is_set_taboo = False
                            break

                if(not is_set_taboo):
                    t = []
                
                taboos = taboos + t

    return list(set(corners + taboos))

def find_manhattan(p1, p2):
    return sum(abs(sum1-sum2) for sum1, sum2 in zip(p1,p2))

def move_towards(point : tuple , deltaDir : tuple) -> tuple:
    if(len(point) != 2  or len(deltaDir) !=2 ):
        raise ValueError("Coordinate Should Have two values.")
    return (point[0] + deltaDir[0], point[1] + deltaDir[1])



def solve_weight_sokoban_bfs(warehouse: Warehouse):
    taboocells = find_taboo_cells(warehouse)

    for box in warehouse.boxes:
        for taboo in taboocells:
            if box == taboo:
                return 'Impossible', None
    
    sp = SokobanPuzzle(warehouse, taboocells)

    solve_bfs, frontier = Search.breadth_first_search(sp)

    if solve_bfs is None:
        return 'Impossible', None
    seq_bfs = sp.get_seq_from_goalnode(solve_bfs)

    return seq_bfs, solve_bfs.path_cost, frontier



def solve_weight_sokoban_dfs(warehouse: Warehouse):
    taboocells = find_taboo_cells(warehouse)

    for box in warehouse.boxes:
        for taboo in taboocells:
            if box == taboo:
                return 'Impossible', None
    
    sp = SokobanPuzzle(warehouse, taboocells)

    solve_dfs, frontier = Search.depth_first_search(sp)

    if solve_dfs is None:
        return 'Impossible', None
    seq_dfs = sp.get_seq_from_goalnode(solve_dfs)

    return seq_dfs, solve_dfs.path_cost, frontier

def solve_weight_sokoban_ucs(warehouse: Warehouse):
    taboocells = find_taboo_cells(warehouse)

    for box in warehouse.boxes:
        for taboo in taboocells:
            if box == taboo:
                return 'Impossible', None
    
    sp = SokobanPuzzle(warehouse, taboocells)

    solve_ucs, frontier = Search.uniform_cost_search(sp)

    if solve_ucs is None:
        return 'Impossible', None
    seq_ucs = sp.get_seq_from_goalnode(solve_ucs)

    return seq_ucs, solve_ucs.path_cost, frontier

def solve_weight_sokoban_as(warehouse: Warehouse):
    taboocells = find_taboo_cells(warehouse)

    for box in warehouse.boxes:
        for taboo in taboocells:
            if box == taboo:
                return 'Impossible', None
    
    sp = SokobanPuzzle(warehouse, taboocells)

    solve_as, frontier = Search.astar_search(sp)

    if solve_as is None:
        return 'Impossible', None
    seq_as = sp.get_seq_from_goalnode(solve_as)

    return seq_as, solve_as.path_cost, frontier

