class MapParser:
    def __init__(self):
        pass

    def parse_line(self, line:str, map: list[list], char:str, replace_char: str):
        i = 1
        parsed_line = line.split(' ')
        while i < len(parsed_line):
            x = int(parsed_line[i])
            y = int(parsed_line[i + 1])
            if map[x - 1][y - 1] != ' ':
                map[x - 1][y - 1] = replace_char
            else:
                map[x - 1][y - 1] = char
            i += 2


    def __call__(self, filename: str):
        with open(filename, 'r') as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]

        [width, height] = lines[0].split(' ')
        map = [[' ' for _ in range(int(width))] for _ in range(int(height))]

        player_coordinate = lines[-2].split(' ')
        weights = [int(weight) for weight in lines[-1].split(' ')]


        if map[int(player_coordinate[0]) - 1][int(player_coordinate[1]) - 1] == ' ':
            map[int(player_coordinate[0]) - 1][int(player_coordinate[1]) - 1] = '@'

        else:
            map[int(player_coordinate[0]) - 1][int(player_coordinate[1]) - 1] = '+'

        self.parse_line(lines[1], map, '#', '#')
        self.parse_line(lines[2], map, '$', '*')
        self.parse_line(lines[3], map, '.', '*')

        return map, weights





