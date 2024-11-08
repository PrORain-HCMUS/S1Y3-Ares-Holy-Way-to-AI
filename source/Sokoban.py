import operator, functools
from MapParser import MapParser

def find_1D_iterator(line:str, char:str):
    pos = 0
    pos = line.find(char, pos)
    while pos != -1:
        yield pos
        pos = line.find(char, pos + 1)

def find_2D_iterator(lines:list[str], char):
    for index, line in enumerate(lines):
        for pos in find_1D_iterator(line, char):
            yield (pos, index)

class Warehouse:
    def copy(self, worker = None, boxes = None, weights = None):
        clone = Warehouse()
        clone.worker = worker or self.worker
        clone.boxes = boxes or self.boxes
        clone.weights = weights or self.weights
        clone.targets = self.targets
        clone.walls = self.walls
        clone.ncols = self.ncols
        clone.nrows = self.nrows
        return clone
    
    def from_string(self, warehouse_str: str):
        lines = warehouse_str.split(sep='\n')
        self.from_lines(lines)

    def load_warehouse(self, filepath: str):
        map, weights = MapParser()(filename=filepath)
        self.weights = weights
        lines = [''.join(row) for row in map]
        self.from_lines(lines)

    def from_lines(self, lines:list[str]):
        first_row_brick, first_col_brick = None, None
        for row, line in enumerate(lines):
            brick_column = line.find('#')
            if brick_column >= 0:
                if first_row_brick is None:
                    first_row_brick = row
                if first_col_brick is None:
                    first_col_brick = brick_column
                else:
                    first_col_brick = min(first_col_brick, brick_column)
        
        if first_row_brick is None:
            raise ValueError('Warehouse with no walls!')
        
        canonical_lines = [line[first_col_brick:]
                           for line in lines[first_row_brick:] if line.find('#') >= 0]

        self.ncols = 1 + max(line.rfind('#') for line in canonical_lines)
        self.nrows = len(canonical_lines)
        self.extract_locations(canonical_lines)


    def save_warehouse(self, filepath: str):
        with open(filepath, 'w') as f:
            f.write(self.__str__())

    def extract_locations(self, lines: list[str]):
        workers = list(find_2D_iterator(lines, '@'))
        workers_on_a_target = list(find_2D_iterator(lines, '+'))

        assert len(workers) + len(workers_on_a_target) == 1
        if len(workers) == 1:
            self.worker = workers[0]
        self.boxes = list(find_2D_iterator(lines, '$'))
        self.targets = list(find_2D_iterator(lines, '.'))
        targets_with_boxes = list(find_2D_iterator(lines, '*'))
        self.boxes += targets_with_boxes
        self.boxes.sort(key = lambda p: (p[1], p[0]))
        self.targets += targets_with_boxes

        if len(workers_on_a_target) == 1:
            self.worker = workers_on_a_target[0]
            self.targets.append(self.worker)
        self.walls = list(find_2D_iterator(lines, '#'))

        assert len(self.boxes) == len(self.targets)

    def __str__(self):
        X, Y = zip(*self.walls)
        x_size, y_size = 1 + max(X), 1 + max(Y)
        visit = [[" "] * x_size for _ in range(y_size)]

        for (x, y) in self.walls:
            visit[y][x] = '#'
        for (x, y) in self.targets:
            visit[y][x] = '.'

        if visit[self.worker[1]][self.worker[0]] == '.':
            visit[self.worker[1]][self.worker[0]] = '+'
        else:
            visit[self.worker[1]][self.worker[0]] = '@'
        
        for (x, y) in self.boxes:
            if visit[y][x] == '.':
                visit[y][x] = '*'
            else:
                visit[y][x] = '$'
        

        return '\n'.join([''.join(line) for line in visit])
    
    def __hash__(self):
        return hash(self.worker) ^ functools.reduce(operator.xor, [hash(box) for box in self.boxes])

filepath = r"./input/input_10_10_2_4.txt"

if __name__ == "__main__":
    a = (1, 2)
    print(a[0], a[1])




