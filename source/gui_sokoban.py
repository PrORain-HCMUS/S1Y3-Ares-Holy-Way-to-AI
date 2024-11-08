import tkinter as tk, os, time, tracemalloc
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk, ImageDraw
from tkinter import font as tkFont
from Sokoban import Warehouse
from SokobanSolver import solve_weight_sokoban_bfs, solve_weight_sokoban_dfs, solve_weight_sokoban_ucs, solve_weight_sokoban_as


__author__ = "Quatermelon"
__version__ = "1.0"

class AboutPage:
    def __init__(self, root, app_root_folder):
        self.root = root
        self.app_root_folder = app_root_folder
        
        # Sử dụng Canvas thay vì Frame
        self.canvas = tk.Canvas(self.root, bg="white", width=1000, height=600)
        self.canvas.place(relwidth=1, relheight=1)  # Đặt canvas phủ toàn bộ màn hình

        # Tải ảnh nền
        self.image = self.load_image("images/background/about/about.png", (1000, 600))
        
        # Vẽ ảnh nền lên Canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        
        # Tạo nút "Back" sử dụng Canvas
        back_button = tk.Button(self.root, text="Back", command=self.back_to_home, font=("Arial", 14, "bold"))
        back_button_window = self.canvas.create_window(500, 550, window=back_button)  # Đặt nút tại vị trí (500, 550)
    
    def load_image(self, filepath: str, resize: tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path).convert('RGBA')

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)

    def back_to_home(self):
        self.canvas.destroy()  # Xóa canvas hiện tại
        Home(self.root, self.app_root_folder) 


class MapView:
    def __init__(self, app_root_folder, map_file, parent_canvas, on_click_callback):
        self.app_root_folder = app_root_folder
        self.warehouse = self.load_warehouse(map_file)
        self.parent_canvas = parent_canvas
        self.on_click_callback = on_click_callback
        self.cells = {}
        
        self.box_width = min(350 // self.warehouse.nrows, 350 // self.warehouse.ncols)


        self.images = {
            'wall': self.load_image('images/cell/wall.png', (self.box_width, self.box_width)),
            'space': self.load_image('images/cell/in_space.png', (self.box_width, self.box_width))
        }

        self.frame = tk.Frame(self.parent_canvas, width=350, height=350)
        self.frame.grid_propagate(False)

    def load_warehouse(self, warehouse_path: str):
        try:
            warehouse = Warehouse()
            warehouse.load_warehouse(warehouse_path)
            return warehouse
        except Exception as e:
            return None

    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        try:
            image = Image.open(path).convert('RGBA')
            if resize:
                image = image.resize(resize, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            return None
    
    def make_cell(self, cell_image, row, col):
        canvas = tk.Canvas(self.frame, width=self.box_width, height=self.box_width, highlightthickness=0, bd=0)
        canvas.create_image(0, 0, anchor=tk.NW, image=cell_image)
        canvas.grid(row=row, column=col)
        canvas.bind("<Button-1>", lambda e: self.on_cell_click())
        return canvas

    def on_cell_click(self):
    # Gọi lại sự kiện click map từ lớp OptionsPage
        if hasattr(self, 'on_click_callback') and callable(self.on_click_callback):
            self.on_click_callback()

    def fresh_display(self):
        if self.warehouse is None:
            print("No warehouse data to display.")
            return self.frame
        
        for row in range(self.warehouse.nrows):
            for col in range(self.warehouse.ncols):
                position = (col, row)
                if position in self.warehouse.walls:
                    # print(f"Placing wall at {position}")
                    self.cells[position] = self.make_cell(self.images['wall'], row, col)
                else:
                    # print(f"Placing space at {position}")
                    self.cells[position] = self.make_cell(self.images['space'], row, col)

        return self.frame

class OptionsPage:
    def __init__(self, root, app_root_folder):
        self.root = root
        self.app_root_folder = app_root_folder
        self.warehouse_files = self.load_warehouse_files()
        self.current_page = 0
        self.clouds = []
        self.clouds_position = [0, 750, 1000]
        self.cloud_speed = 2
        self.animation_running = True


        self.image_dict = {
            'background': self.load_image('images/background/options/background.png', resize=(1000, 600)),
            'title': self.load_image('images/background/options/title.png', resize=(300, 25)),
            'next': self.load_image('images/background/util/next.png', resize=(30, 50)),
            'prev': self.load_image('images/background/util/prev.png', resize=(30, 50)),
            'back': self.load_image('images/background/util/back.png', resize=(75, 50)),
            'clouds': [self.load_image(f'images/background/util/cloud/{i}.png') for i in range(3)],
        }

        self.canvas = tk.Canvas(self.root, width=1000, height=600)
        self.canvas.pack()

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_dict['background'])
        self.canvas.create_image(300, 75, anchor=tk.CENTER, image=self.image_dict['title'])
        
        self.back_button = self.canvas.create_image(50, 550, anchor=tk.CENTER, image=self.image_dict['back'])
        self.canvas.tag_bind(self.back_button, "<Button-1>", lambda event: self.go_back())
        self.canvas.tag_bind(self.back_button, "<Enter>", lambda event: self.canvas.config(cursor='hand2'))
        self.canvas.tag_bind(self.back_button, "<Leave>", lambda event: self.canvas.config(cursor=''))

        self.draw_clouds()
        self.animate_clouds()

        self.show_map_options()
    
    def draw_clouds(self):
        for i in range(3):
            cloud = self.canvas.create_image(self.clouds_position[i], 100, anchor=tk.CENTER, image = self.image_dict['clouds'][i])
            self.clouds.append(cloud)

    def animate_clouds(self):
        if not self.animation_running or not self.canvas:
            return
        for i in range(3):
            self.canvas.move(self.clouds[i], self.cloud_speed, 0)
            pos = self.canvas.coords(self.clouds[i])[0]

            if pos > 1920:
                self.canvas.move(self.clouds[i], -1920 - 100, 0)

        self.root.after(50, self.animate_clouds)

    def stop_animation(self):
        self.animation_running = False


    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path).convert('RGBA')

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)
    
    def load_warehouse_files(self):
        map_folder = os.path.join(self.app_root_folder, 'input')
        return [os.path.join(map_folder, file) for file in os.listdir(map_folder)]

    def show_map_options(self):
        self.canvas.delete('input')
        self.canvas.delete('navigation_buttons')
        self.map_views = []
        start = self.current_page * 2
        end = start + 2
        displayed_warehouses = self.warehouse_files[start: end]

        for index, warehouse_path in enumerate(displayed_warehouses):
            x_position = 450 * index + 100
            map_view = MapView(self.app_root_folder, warehouse_path, self.canvas, lambda path=warehouse_path: self.start_game(path))
            self.map_views.append(map_view)
            map_frame = map_view.fresh_display()
            if map_frame:
                self.canvas.create_window(x_position, 130, anchor=tk.NW, window=map_frame, tags='input')
                self.canvas.update_idletasks()

        total_pages = (len(self.warehouse_files) + 1) // 2
        
        if self.current_page > 0:
            prev_button = self.canvas.create_image(50, 300, anchor=tk.CENTER, image=self.image_dict['prev'], tags='navigation_buttons')
            self.canvas.tag_bind(prev_button, "<Button-1>", lambda event: self.show_prev())
            self.canvas.tag_bind(prev_button, "<Enter>", lambda event: self.canvas.config(cursor='hand2'))
            self.canvas.tag_bind(prev_button, "<Leave>", lambda event: self.canvas.config(cursor=''))

        if self.current_page < total_pages - 1:
            next_button = self.canvas.create_image(950, 300, anchor=tk.CENTER, image=self.image_dict['next'], tags='navigation_buttons')
            self.canvas.tag_bind(next_button, "<Button-1>", lambda event: self.show_next())
            self.canvas.tag_bind(next_button, "<Enter>", lambda event: self.canvas.config(cursor='hand2'))
            self.canvas.tag_bind(next_button, "<Leave>", lambda event: self.canvas.config(cursor=''))

    def show_next(self):
        total_pages = (len(self.warehouse_files) + 1) // 2
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.show_map_options()

    def show_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_map_options()


    def go_back(self):
        self.stop_animation()
        self.canvas.delete('input')
        self.canvas.delete('navigation_buttons')
        self.canvas.destroy()
        Home(self.root, self.app_root_folder)

    def start_game(self, warehouse_path):
        self.stop_animation()
        self.canvas.delete('input')
        self.canvas.delete('navigation_buttons')
        self.canvas.destroy()
        GamePage(self.root, self.app_root_folder, warehouse_path)

class MainGame:
    def __init__(self, frame: tk.Frame, cells: dict, root, app_root_folder: str, warehouse_path: str):
        self.parent_frame = frame
        self.warehouse_path = warehouse_path
        self.warehouse = self.load_warehouse(self.warehouse_path)
        self.cells = cells
        self.root = root
        self.app_root_folder = app_root_folder
        self.solution = None
        self.font = tkFont.Font(family="ArcadeGamer", size=15)
        
        self.cell_size = min(550 // self.warehouse.nrows, 550 // self.warehouse.ncols)

        self.grid_frame = tk.Frame(self.parent_frame, width=550, height=550)
        self.grid_frame.place(x = 900 - 550, y=10, width=550, height=550)


        self.image_dict = {
            'ares': {
                'go_ahead': [self.load_image(f'images/ares/go_ahead/{i}.png', (self.cell_size, self.cell_size)) for i in range(4)],
                'go_back': [self.load_image(f'images/ares/go_back/{i}.png', (self.cell_size, self.cell_size)) for i in range(4)],
                'go_left': [self.load_image(f'images/ares/go_left/{i}.png', (self.cell_size, self.cell_size)) for i in range(4)],
                'go_right': [self.load_image(f'images/ares/go_right/{i}.png', (self.cell_size, self.cell_size)) for i in range(4)],
                'stand': self.load_image('images/ares/stand/0.png', (self.cell_size, self.cell_size)),
            },
            'wall': self.load_image('images/cell/wall.png', (self.cell_size, self.cell_size)),
            'box': self.load_image('images/cell/box.png', (self.cell_size, self.cell_size)),
            'box_on_target': self.load_image('images/cell/right_box.png', (self.cell_size, self.cell_size)),
            'target': self.load_image('images/cell/dock.png', (self.cell_size, self.cell_size)),
            'in_space': self.load_image('images/cell/in_space.png', (self.cell_size, self.cell_size)),
            'out_space': self.load_image('images/cell/out_space.png', (self.cell_size, self.cell_size)),
            'victory_title': self.load_image('images/background/util/victory.png', (740, 100))
        }
        
        self.direction_offset = {
            'Left': (-1, 0),
            'Right': (1, 0),
            'Up': (0, -1),
            'Down': (0, 1)
        }


    def load_warehouse(self, warehouse_path: str):
        try:
            warehouse = Warehouse()
            warehouse.load_warehouse(warehouse_path)
            return warehouse
        except:
            return None

    def get_box_weight(self, x, y):
        try:
            w = self.warehouse.weights[self.warehouse.boxes.index((x, y))]
        except:
            w = 0
        return w

    def make_cell(self, cell_image, row, col, box_weight=None):
        canvas = tk.Canvas(self.grid_frame,
                           width=self.cell_size,
                           height=self.cell_size,
                           highlightthickness=0,
                           bd=0)
        canvas.create_image(0, 0, anchor=tk.NW, image=cell_image)
        if box_weight is not None:
            canvas.create_text(self.cell_size // 2, self.cell_size // 2, text=str(box_weight), fill='red', font=(self.font, 15, 'bold'))
        canvas.grid(row=row, column=col)
        return canvas

    def clear_level(self):
        for cell in self.cells.values():
            cell.destroy()
        self.cells.clear()
        self.warehouse = self.load_warehouse(self.warehouse_path)

    def start_level(self):
        self.root.title(f"Ares: Holy Way to AI - {os.path.basename(self.warehouse_path).split('.')[0]}")
        self.fresh_display()

    def clean_cell(self, x, y):
        if (x, y) in self.cells:
            self.cells[(x, y)].destroy()
            del self.cells[(x, y)]

    def fresh_display(self):
        for row in range(self.warehouse.nrows):
            for col in range(self.warehouse.ncols):
                position = (col, row)

                if position in self.warehouse.walls:
                    self.cells[position] = self.make_cell(self.image_dict['wall'], row, col)
                elif position in self.warehouse.targets:
                    self.cells[position] = self.make_cell(self.image_dict['target'], row, col)
                elif position in self.warehouse.boxes:
                    if position in self.warehouse.targets:
                        self.cells[position] = self.make_cell(self.image_dict['box_on_target'], row, col, self.get_box_weight(col, row))
                    else:
                        self.cells[position] = self.make_cell(self.image_dict['box'], row, col, self.get_box_weight(col, row))
                elif position == self.warehouse.worker:
                    self.cells[position] = self.make_cell(self.image_dict['ares']['stand'], row, col)
                else:
                    self.cells[position] = self.make_cell(self.image_dict['in_space'], row, col)


    def move_player(self, direction: str):
        map_direction = {
            'l': 'Left',
            'r': 'Right',
            'u': 'Up',
            'd': 'Down'
        }
        if direction in map_direction.keys():
            direction = map_direction[direction]
        x, y = self.warehouse.worker
        xy_offset = self.direction_offset[direction]
        next_x, next_y = x + xy_offset[0], y + xy_offset[1]

        if (next_x, next_y) in self.warehouse.walls:
            return
        if (next_x, next_y) in self.warehouse.boxes:
            if not self.try_move_box((next_x, next_y), (next_x + xy_offset[0], next_y + xy_offset[1])):
                return

        self.clean_cell(x, y)
        self.clean_cell(next_x, next_y)

        self.cells[(next_x, next_y)] = self.make_cell(self.image_dict['ares']['stand'], next_y, next_x)
        self.warehouse.worker = (next_x, next_y)

        if (x, y) in self.warehouse.targets:
            self.cells[(x, y)] = self.make_cell(self.image_dict['target'], y, x)
        else:
            self.cells[(x, y)] = self.make_cell(self.image_dict['in_space'], y, x)

        if all(z in self.warehouse.targets for z in self.warehouse.boxes):
            self.show_victory_screen()
        


    def show_victory_screen(self):
        self.canvas = tk.Canvas(self.parent_frame, width=1000, height=600, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_image(130, 200, anchor=tk.NW, image=self.image_dict['victory_title'])
        back_button = tk.Button(self.parent_frame, text="Back", command=self.destroy_canvas, cursor='hand2', width=20, pady=5, font=(self.font, 20, 'bold'))
        self.canvas.create_window(490, 400, window=back_button)

    def destroy_canvas(self):
        self.canvas.destroy()
        self.grid_frame.destroy()
        self.parent_frame.destroy()
        Home(self.root, self.app_root_folder)


    def try_move_box(self, location: tuple, next_location: tuple):
        x, y = location
        next_x, next_y = next_location

        if (next_x, next_y) not in self.warehouse.walls and (next_x, next_y) not in self.warehouse.boxes:
            if (next_x, next_y) in self.cells:
                self.clean_cell(next_x, next_y)

            if (next_x, next_y) in self.warehouse.targets:
                self.cells[(next_x, next_y)] = self.make_cell(self.image_dict['box_on_target'], next_y, next_x, self.get_box_weight(x, y))
            else:
                self.cells[(next_x, next_y)] = self.make_cell(self.image_dict['box'], next_y, next_x, self.get_box_weight(x, y))
            
            self.clean_cell(x, y)
            if (x, y) in self.warehouse.targets:
                self.cells[(x, y)] = self.make_cell(self.image_dict['target'], y, x)
            else:
                self.cells[(x, y)] = self.make_cell(self.image_dict['in_space'], y, x)

            bi = self.warehouse.boxes.index((x, y))
            self.warehouse.boxes[bi] = (next_x, next_y)

            return True
        return False

    def key_handler(self, event):
        if event.keysym in ('Left', 'Right', 'Up', 'Down'):
            self.move_player(event.keysym)
        if event.keysym in ('r', 'R'):
            self.clear_level()
            self.start_level()
    
    def solve_puzzle(self, method: str):
        if self.warehouse is None:
            print("Load a warehouse!!")
            return
        print("Starting to analyze to find solution...")
        t0 = time.time()
        tracemalloc.start()
        if method == "BFS":
            solution, total_cost, frontier = solve_weight_sokoban_bfs(self.warehouse)
        elif method == "DFS":
            solution, total_cost, frontier = solve_weight_sokoban_dfs(self.warehouse)
        elif method == "UCS":
            solution, total_cost, frontier = solve_weight_sokoban_ucs(self.warehouse)
        else:
            solution, total_cost, frontier = solve_weight_sokoban_as(self.warehouse)
        t1 = time.time()

        steps = len(solution) if solution != "Impossible" else 0
        total_weight = sum(self.get_box_weight(x, y) for x, y in self.warehouse.boxes)
        nodes_generated = len(frontier)
        current, _ = tracemalloc.get_traced_memory()
        memory_used = current

        print(f"Analysis took {t1 - t0:.6f} seconds")
        if solution == "Impossible":
            self.solution = None
            print("No solution found!")
        else:
            self.save_solution_to_file(method, steps, total_weight, nodes_generated, t1 - t0, memory_used, solution)
            self.solution = solution
            print(f"Solution found with a cost of {total_cost}\n", solution, '\n')

        tracemalloc.stop()

    def play_solution(self):
        if self.solution and len(self.solution) > 0:
            self.move_player(self.solution.pop(0))
            self.parent_frame.after(300, self.play_solution)

    def save_solution_to_file(self, method, steps, total_weight, nodes_generated, time_taken, memory_used, solution):
        output_folder = os.path.join(self.app_root_folder, "output")
        print(output_folder)
        os.makedirs(output_folder, exist_ok=True)
        
        output_file = os.path.join(output_folder, f"{os.path.basename(self.warehouse_path)}")
        
        solution_str = ''.join(solution)

        with open(output_file, 'w') as file:
            file.write(f"{method}\n")
            file.write(f"Steps: {steps}, Total Weight: {total_weight}, Nodes Generated: {nodes_generated}, ")
            file.write(f"Time Taken: {time_taken:.6f}s, Memory Used: {memory_used} bytes\n")
            file.write(solution_str)
        
        print(f"Solution saved to {output_file}")


    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path)
        if resize:
            image = image.resize(resize, Image.LANCZOS)
        return ImageTk.PhotoImage(image)

class GamePage:
    def __init__(self, root, app_root_folder, warehouse_path):
        self.root = root
        self.app_root_folder = app_root_folder
        self.warehouse_path = warehouse_path
        self.image = self.load_image("images/background/map/0.png", resize=(1000, 600))
        self.font = tkFont.Font(family="ArcadeGamer", size=15)
        
        self.dominant_color = self.get_dominant_color(os.path.join(self.app_root_folder, "images/background/map/0.png"))

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.background_label = tk.Label(self.frame, image=self.image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.small_frame = tk.Frame(self.frame, width=250, height=250, bg=self.dominant_color)
        self.small_frame.place(x=50, y=0, anchor="nw", width=250, height=250)
        
        self.draw_game_controls()
        self.draw_map()

    def get_dominant_color(self, image_path):
        image = Image.open(image_path)

        image = image.convert("RGB")
        
        width, height = image.size

        top_half = image.crop((0, 0, width, height // 2))

        pixels = top_half.getdata()
        
        r, g, b = 0, 0, 0
        for pixel in pixels:
            r += pixel[0]
            g += pixel[1]
            b += pixel[2]
        
        total_pixels = len(pixels)
        if total_pixels > 0:
            r //= total_pixels
            g //= total_pixels
            b //= total_pixels

        return f'#{r:02x}{g:02x}{b:02x}'

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return (r, g, b)

    def get_text_color(self, dominant_color):
        r, g, b = self.hex_to_rgb(dominant_color)
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        return 'black' if brightness > 128 else 'white'

    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path)

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)

    def draw_game_controls(self):
        text_color = self.get_text_color(self.dominant_color)
        control_label = tk.Label(self.small_frame, text="GAME CONTROLS", bg=self.dominant_color, font=(self.font, 20, 'bold'), fg=text_color)
        control_label.pack(pady=5)
        
        self.algorithm_label = tk.Label(self.small_frame, text="ALGORITHMS: UNKNOWN", bg=self.dominant_color, font=(self.font, 14, 'bold'), fg=text_color)
        self.algorithm_label.pack(pady=5)


        button_frame = tk.Frame(self.small_frame, bg=self.dominant_color)
        button_frame.pack(pady=5)

        restart_button = tk.Button(button_frame, text="Restart", command=self.restart_game, font=(self.font, 10), cursor="hand2")
        restart_button.pack(side=tk.LEFT, padx=5)

        quit_button = tk.Button(button_frame, text="Quit", command=self.quit_game, font=(self.font, 10), cursor="hand2")
        quit_button.pack(side=tk.LEFT, padx=5)

        solve_button = tk.Button(self.small_frame, text="Solve", font=(self.font, 10), cursor="hand2")
        solve_button.pack(pady=5)

        self.solve_menu = tk.Menu(solve_button, tearoff=0)
        methods_menu = tk.Menu(self.solve_menu, tearoff=0)
        methods_menu.add_command(label="BFS", command=lambda: self.set_method("BFS"))
        methods_menu.add_command(label="DFS", command=lambda: self.set_method("DFS"))
        methods_menu.add_command(label="UCS", command=lambda: self.set_method("UCS"))
        methods_menu.add_command(label="A*", command=lambda: self.set_method("A*"))

        self.solve_menu.add_cascade(label="Methods", menu=methods_menu)
        self.solve_menu.add_command(label="Plan Action Sequence", command=self.plan_action_sequence, state='disabled')
        self.solve_menu.add_command(label="Play Action Sequence", command=self.play_action_sequence, state='disabled')

        solve_button.config(command=lambda: self.solve_menu.post(solve_button.winfo_rootx(), solve_button.winfo_rooty() + solve_button.winfo_height()))

        for button in (restart_button, solve_button, quit_button):
            button.config(width=7)

    def draw_map(self):
        self.main_game = MainGame(self.frame, {}, self.root, self.app_root_folder, self.warehouse_path)
        self.root.bind_all("<Key>", self.main_game.key_handler)
        self.main_game.start_level()


    def set_method(self, method):
        self.method = method
        self.algorithm_label.config(text=f"ALGORITHM: {self.method}")
        self.solve_menu.entryconfig("Plan Action Sequence", state="normal")
        self.solve_menu.entryconfig("Play Action Sequence", state="normal")

    def plan_action_sequence(self):
        if self.method:
            print("Planning action sequence with", self.method)
            self.main_game.solve_puzzle(self.method)

    def play_action_sequence(self):
        if self.method:
            print("Playing action sequence with", self.method)
            self.main_game.play_solution()

    def restart_game(self):
        print("Game Restarted")
        self.main_game.clear_level()
        self.main_game.start_level()

    def solve(self):
        print(f"Solving with {self.method}")


    def quit_game(self):
        self.frame.destroy()
        Home(self.root, self.app_root_folder)

class Home:
    def __init__(self, root, app_root_folder):
        self.root = root
        self.app_root_folder = app_root_folder

        self.clouds = []
        
        self.clouds_position = [0, 750, 1000]
        self.cloud_speed = 2
        self.animation_running = True


        self.canvas = tk.Canvas(self.root, width=1000, height=600)
        self.canvas.pack()

        self.image_dict = {
            'background': self.load_image('images/background/home/background.png', resize=(1000, 600)),
            'moon': self.load_image('images/background/home/moon.png', resize=(100, 100)),
            'title': self.load_image('images/background/home/title.png', resize=(500, 150)),
            'clouds': [self.load_image(f'images/background/util/cloud/{i}.png') for i in range(3)],
            'play': self.load_image('images/background/home/play.png', resize=(200, 70)),
            'about': self.load_image('images/background/home/about.png',resize=(300, 70))
        }

        self.draw_elements()

        play_button = tk.Button(self.root, image=self.image_dict['play'], command=self.go_to_options, cursor='hand2')
        about_button = tk.Button(self.root, image=self.image_dict['about'], command=self.go_to_about, cursor='hand2')

        play_button.place(x=500, y=360, anchor=tk.CENTER)
        about_button.place(x=500, y=460, anchor=tk.CENTER)
        self.add_press_effect(play_button)
        self.add_press_effect(about_button)

        self.draw_clouds()
        self.animate_clouds()

    def load_image(self, filepath:str, resize:tuple = None):
        path = os.path.join(self.app_root_folder, filepath)
        image = Image.open(path)

        if resize:
            image = image.resize(resize, Image.LANCZOS)

        return ImageTk.PhotoImage(image)

    def go_to_options(self):
        self.stop_animation()
        self.canvas.destroy()
        OptionsPage(self.root, self.app_root_folder)

    def go_to_about(self):
        self.stop_animation()
        self.canvas.destroy()
        AboutPage(self.root, self.app_root_folder)

    def add_press_effect(self, button):
        def on_press(event):
            button.config(relief="sunken", padx=3, pady=3)

        def on_release(event):
            button.config(relief="raised", padx=5, pady=5)

        button.bind("<ButtonPress-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)

    def draw_elements(self):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_dict['background'])
        self.canvas.create_image(400, 80, anchor=tk.CENTER, image=self.image_dict['moon'])
        self.canvas.create_image(500, 220, anchor=tk.CENTER, image=self.image_dict['title'])


    def draw_clouds(self):
        for i in range(3):
            cloud = self.canvas.create_image(self.clouds_position[i], 100, anchor=tk.CENTER, image = self.image_dict['clouds'][i])
            self.clouds.append(cloud)

    def animate_clouds(self):
        if not self.animation_running or not self.canvas:
            return
        for i in range(3):
            self.canvas.move(self.clouds[i], self.cloud_speed, 0)
            pos = self.canvas.coords(self.clouds[i])[0]

            if pos > 1920:
                self.canvas.move(self.clouds[i], -1920 - 100, 0)

        self.root.after(50, self.animate_clouds)

    def stop_animation(self):
        self.animation_running = False

if __name__ == '__main__':
    root  = tk.Tk()
    app_root_folder = os.getcwd()
    canvas = tk.Canvas(root, width=1000, height=600)
    root.geometry('1000x600')
    root.title("Ares: Holy Way to AI")
    root.iconphoto(
        False,
        tk.PhotoImage(file=os.path.join(app_root_folder, 'images/ares/stand/0.png'))
    )
    home_page = Home(root, app_root_folder)

    root.mainloop()

    # root = tk.Tk()
    # app_root_folder = os.getcwd()
    # map_file_path = "D:/Project/ai_fundamental/Ares/input/input_10_10_3_1.txt"
    # map_view = MapView(app_root_folder, map_file_path, root)
    # frame = map_view.fresh_display()
    # frame.pack()
    # root.mainloop()