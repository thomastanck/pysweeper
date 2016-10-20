import tkinter
from PIL import Image, ImageTk
import threading
import time

class Application(tkinter.Frame):
    timer_threads = []
    def createWidgets(self):
        self.main_container = MainContainer(self)        
        
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.timing = False

        self.bind("<F2>", self.hit_f2)
        self.bind("<F3>", self.hit_f3)
        self.focus_set()
        
        self.reset = self.speed_game_reset
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    i = 0
    def hit_f2(self, e):
        print(self.i, "hit f2")
        self.i += 1
        self.speed_game(self.board.board_width*self.board.board_height//2)

    def hit_f3(self, e):
        self.reset()


    def reset_board(self):
        board = self.board
        width = board.board_width
        height = board.board_height
        for i in range(height):
            for j in range(width):
                board.reset_depressed()
                board.set_tile(i, j, "unopened")

    def speed_game(self, n):
        width = self.board.board_width
        height = self.board.board_height
        area = width*height
        if not 0 <= n < area:
            n = 0
        import random
        squares = [0]*area
        i = 0
        while i < n: 
            rand = random.randint(0, area-1)
            if not squares[rand]:
                squares[rand] = 1
                i += 1
        self.speed_game_grid = squares
        self.speed_game_reset()
        self.start_timer()

    def speed_game_reset(self):
        width = self.board.board_width
        height = self.board.board_height
        area = width*height
        squares = self.speed_game_grid
        for i in range(area):
            row = i//width
            col = i%width
            tile = "unopened" if squares[i] else "tile_0"
            self.board.draw_tile(row, col, tile)
        self.board.update_canvas()

    def start_timer(self):
        self.start_time = time.time()
        self.timing_mode = True
        self.timer_value = 0

        def timer_thread():
            while self.timing_mode:
                elapsed = int(time.time() - self.start_time)+1
                if self.timer_value != elapsed:
                    self.main_container.sub_frame.set_timer(elapsed)
                time.sleep(0.0101)
        if not self.timer_threads:
            new_thread = threading.Thread(target=timer_thread)            
            self.timer_threads.append(new_thread)
            new_thread.start()

    def stop_timer(self):
        self.timing_mode = False
        threads_to_remove = []
        for timer_thread in self.timer_threads:
            if not timer_thread.is_alive():
                threads_to_remove.append(timer_thread)
        print("Threads to remove:", threads_to_remove)
        for thread in threads_to_remove:
            self.timer_threads.remove(thread)
                

    def on_close(self):
        self.kill_timer()
        self.master.destroy()

    def kill_timer(self):
        self.stop_timer()
        for timer_thread in self.timer_threads:
            timer_thread.join()
            
        
        

class MainContainer(tkinter.Frame):
    def create_widgets(self):
        self.sub_frame = GameDisplay(self, 50, 100)
        self.master.board = self.sub_frame.board

    def __init__(self, master=None):
        super().__init__(master, width=200, height=200, background="green")
        self.pack()
        self.config(borderwidth=0)
        self.create_widgets()

    def key_pressed(self, e):
        print(e)

class GameDisplay(tkinter.Frame):
    border_images = {}
    def create_widgets(self):
        grid_row = 0
        self.border_top_left = tkinter.Canvas(self, width=12, height=15,
                                              highlightthickness=0)
        self.border_top = tkinter.Canvas(self, width=16*self.board_width,
                                         height=15, highlightthickness=0)
        self.border_top_right = tkinter.Canvas(self, width=12, heigh=15,
                                               highlightthickness=0)
        self.border_top_left.grid(row=grid_row, column=0)
        self.border_top.grid(row=grid_row, column=1)
        self.border_top_right.grid(row=grid_row, column=2)
        grid_row = 1
        self.border_panel_left = tkinter.Canvas(self, width=12, height=26,
                                             highlightthickness=0)
        self.panel = Panel(self, board_width=self.board_width)
        self.border_panel_right = tkinter.Canvas(self, width=12, height=26,
                                                 highlightthickness=0)
        self.border_panel_left.grid(row=grid_row, column=0)
        self.panel.grid(row=grid_row, column=1, sticky="nesw")
        self.border_panel_right.grid(row=grid_row, column=2)
        
        grid_row = 2
        self.border_mid_left = tkinter.Canvas(self, width=12, height=14,
                                              highlightthickness=0)
        self.border_mid = tkinter.Canvas(self, width=16*self.board_width,
                                         height=14, highlightthickness=0)
        self.border_mid_right = tkinter.Canvas(self, width=12, height=14,
                                               highlightthickness=0)
        self.border_mid_left.grid(row=grid_row, column=0)
        self.border_mid.grid(row=grid_row, column=1)
        self.border_mid_right.grid(row=grid_row, column=2)
        
        self.border_left = tkinter.Canvas(self, width=12,
                                          height=16*self.board_height)
        self.border_left.config(highlightthickness=0)
        self.board = Board(self, self.board_width, self.board_height)
        self.border_right = tkinter.Canvas(self, width=12,
                                           height=16*self.board_height)
        self.border_right.config(highlightthickness=0)

        grid_row = 3
        self.border_left.grid(row=grid_row, column=0)
        self.board.grid(row=grid_row, column=1)
        self.border_right.grid(row=grid_row, column=2)

        grid_row = 4
        self.border_bot_left = tkinter.Canvas(self, width=12, height=12,
                                              highlightthickness=0)
        self.border_bot = tkinter.Canvas(self, width=16*self.board_width,
                                         height=12, highlightthickness=0)
        self.border_bot_right = tkinter.Canvas(self, width=12,
                                               height=12, highlightthickness=0)
        self.border_bot_left.grid(row=grid_row, column=0)
        self.border_bot.grid(row=grid_row, column=1)
        self.border_bot_right.grid(row=grid_row, column=2)

        
        self.init_border()
        

    def init_border(self):
        for key in ('l', 'r', 'bot_l', 'bot', 'bot_r', 'mid_l', 'mid', 'mid_r',
                    'panel_l', 'panel_r', 'top_l', 'top', 'top_r'):
            img = Image.open("images/border_{}.png".format(key))
            self.border_images[key] = ImageTk.PhotoImage(img)
        height = self.board_height
        width = self.board_width
        for i in range(height):
            border = self.border_images['l']
            self.border_left.create_image((0, 16*i), image=border, anchor='nw')
            border = self.border_images['r']
            self.border_right.create_image((0, 16*i), image=border, anchor='nw')
        
        for i in range(width):
            border = self.border_images['top']
            self.border_top.create_image((16*i, 0), image=border, anchor='nw')
            border = self.border_images['mid']
            self.border_mid.create_image((16*i, 0), image=border, anchor='nw')
            border = self.border_images['bot']
            self.border_bot.create_image((16*i, 0), image=border, anchor='nw')
        border = self.border_images['top_l']
        self.border_top_left.create_image((0, 0), image=border, anchor='nw')
        border = self.border_images['top_r']
        self.border_top_right.create_image((0, 0), image=border, anchor='nw')
        border = self.border_images['panel_l']
        self.border_panel_left.create_image((0, 0), image=border, anchor='nw')
        border = self.border_images['panel_r']
        self.border_panel_right.create_image((0, 0), image=border, anchor='nw')
        border = self.border_images['mid_l']
        self.border_mid_left.create_image((0,0), image=border, anchor='nw')
        border = self.border_images['mid_r']
        self.border_mid_right.create_image((0,0), image=border, anchor='nw')
        border = self.border_images['bot_l']
        self.border_bot_left.create_image((0,0), image=border, anchor='nw')
        border = self.border_images['bot_r']
        self.border_bot_right.create_image((0,0), image=border, anchor='nw')
        

    def __init__(self, master, board_width, board_height):
        self.board_width = board_width
        self.board_height = board_height
        super().__init__(master, width=board_width*16+24, height=board_height*16)
        self.pack()
        self.create_widgets()

    def set_timer(self, t):
        self.panel.timer.set_value(t)


class Tile:
    def __init__(self, row, col, state=None):
        self.row = row
        self.col = col
        self.state = state
        

class Board(tkinter.Frame):
    def load_tiles(self):
        tile_images = {}
        self.temporarily_down = []
        tile_names = ["tile_{}".format(i) for i in range(9)]
        for key in tile_names + ["unopened", "flag", "blast", "flag_wrong", "mine"]:
            img = Image.open("images/{}.png".format(key))
            tile_images[key] = img
            img.load()
        self.tile_images = tile_images

        width = self.board_width
        height = self.board_height
        tiles = [[Tile(r, c) for c in range(width)] for r in range(height)]
        self.tiles = tiles

    def __init__(self, master, width, height):
        super().__init__(master)
        self.board_width = width
        self.board_height = height
        self.memory_rgba = Image.new(size=(16*width, 16*height), mode="RGB")
        self.canvas_rgba = Image.new(size=(16*width, 16*height), mode="RGB")
        self.memory_rgba.load()
        self.canvas_image = ImageTk.PhotoImage(self.canvas_rgba)
        self.canvas = tkinter.Canvas(self, width=16*width, height=16*height,
                                     highlightthickness=0)
        self.canvas.pack()
        #self.load_tiles()
        self.load_tiles()
        for col in range(width):
            for row in range(height):
                self.draw_tile(row, col, "unopened")
        self.canvas_image_ref = self.canvas.create_image((0,0), anchor="nw",
                                                         image=self.canvas_image)
        self.update_canvas()
        
        
        self.canvas.bind("<ButtonRelease-1>", self.left_up)
        self.canvas.bind("<ButtonPress-1>", self.mouse_over)
        self.canvas.bind("<B1-Motion>", self.mouse_over)

    def draw_tile(self, row, col, tile_type):
        self.memory_rgba.paste(self.tile_images[tile_type], box=(col*16, row*16))
        self.tiles[row][col].state = tile_type

    def set_tile(self, *args):
        self.draw_tile(*args)
        self.update_canvas()
        

    def update_canvas(self):
        self.canvas_image.paste(self.memory_rgba)
        
        
    def reset_depressed(self, avoid_x=-1, avoid_y=-1):
        add_back = (avoid_x, avoid_y) in self.temporarily_down
        if add_back:
            self.temporarily_down.remove((avoid_x, avoid_y))
        while self.temporarily_down:
            x, y = self.temporarily_down.pop()
            self.set_tile(x, y, "unopened")
        if add_back:
            self.temporarily_down.append((avoid_x, avoid_y))

    def left_up(self, e):
        col = e.x//16
        row = e.y//16
        if (col, row) in self.temporarily_down:
            self.temporarily_down.remove((col,row))
        self.reset_depressed()
        width = self.board_width
        height = self.board_height
        if (0 <= col < width and 0 <= row < height):
            self.set_tile(row, col, "tile_0")

    def mouse_over(self, e):
        col = e.x//16
        row = e.y//16
        width, height = self.board_width, self.board_height
        if not (0 <= col < width and 0 <= row < height):
            # i.e., we've moved off the board
            self.reset_depressed()
        else:        
            tile = self.tiles[row][col]
            self.reset_depressed(row, col)
            if tile.state == "unopened":
                self.temporarily_down.append((row, col))
                self.set_tile(row, col, "tile_0")
        
class Counter(tkinter.Frame):
    border_images = {}
    def create_widgets(self):
        self.digits = []
        display_width = self.display_width
        for i in range(display_width):
            digit = Digit(self)
            digit.grid(row=1, column=i+1)
            self.digits.append(digit)

        self.border_left = tkinter.Canvas(self, width=1, height=25,
                                          highlightthickness=0)
        self.border_left.create_image((0,0), anchor='nw',
                                      image=self.border_images['l'])
        self.border_top = tkinter.Canvas(self, width=13*display_width,
                                         height=1, highlightthickness=0)
        for i in range(display_width):
            self.border_top.create_image((13*i,0), anchor='nw',
                                         image=self.border_images['t'])
        self.border_bot = tkinter.Canvas(self, width=13*display_width,
                                         height=1, highlightthickness=0)
        for i in range(display_width):
            self.border_bot.create_image((13*i,0), anchor='nw',
                                         image=self.border_images['b'])
        self.border_right = tkinter.Canvas(self, width=1, height=25,
                                           highlightthickness=0)
        self.border_right.create_image((0,0), anchor='nw',
                                       image=self.border_images['r'])
        self.border_left.grid(column=0, rowspan=3, row=0)
        self.border_top.grid(column=1, row=0, columnspan=display_width)
        self.border_right.grid(column=display_width+1, rowspan=3, row=0)
        self.border_bot.grid(column=1, row=2, columnspan=display_width)
        
    def __init__(self, master, display_width):
        super().__init__(master)        
        self.display_width = display_width
        self.init_border_images()
        self.create_widgets()

    def init_border_images(self):
        if not self.border_images:
            for key in ('l', 'r', 't', 'b'):
                img = Image.open("images/counter_border_{}.png".format(key))
                self.border_images[key] = ImageTk.PhotoImage(img)

    def set_value(self, n):
        digits = self.display_width
        self.displayed_value = n
        working_width = digits
        sign = 1
        if n < 0:
            working_width = digits-1
            sign = -1
            n = -n
        if abs(n) >= 10**working_width:
            n = 10**working_width-1

        for i in range(digits):
            d = n%10
            n//=10
            self.digits[digits-1-i].set_value(d)
            if n == 0:
                break
        i += 1
        if sign < 0:
            self.digits[digits-1-i].set_value('-')
            i += 1
        for j in range(i, digits):
            self.digits[digits-1-j].set_value('off')
            

class Digit(tkinter.Canvas):
    digits = {}
    def __init__(self, master):
        super().__init__(master, width=13, height=23,
                         highlightthickness=0)
        self.init_digits()
        self.image_reference = self.create_image((0, 0), anchor='nw')
        self.set_value(0)

    def init_digits(self):
        if not self.digits:
            for i in list(range(10)) + ['-', 'off']:
                img = Image.open("images/counter_{}.png".format(i))
                Digit.digits[i] = ImageTk.PhotoImage(img)
                

    def set_value(self, n):        
        self.itemconfig(self.image_reference, image=self.digits[n])

class Panel(tkinter.Frame):
    def __init__(self, master, board_width):
        super().__init__(master, width=board_width*16, height=26)
        self.mine_counter = Counter(self, 8)
        self.mine_counter.grid(row=0, column=0, padx=3)
        self.face_button = FaceButton(self)
        self.face_button.grid(row=0, column=1)
        self.grid_columnconfigure(1, weight=1) # to center face
        self.timer = Counter(self, 8)
        self.timer.grid(row=0, column=2, padx=3)
        self.config(background="#c0c0c0")

        self.mine_counter.set_value(0)
        self.timer.set_value(0)

class FaceButton(tkinter.Frame):
    face_images = {}
    def __init__(self, master):
        super().__init__(master, width=26, height=26)
        if not self.face_images:
            self.init_face_images()
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tkinter.Canvas(self, width=26, height=26,
                                     highlightthickness=0)
        self.canvas.pack()
        self.image_reference = self.canvas.create_image((0,0), anchor='nw')
        self.set_face('happy')

    def init_face_images(self):
        for key in ["happy", "pressed", "blast", "cool"]:
            img = Image.open("images/face_{}.png".format(key))
            self.face_images[key] = ImageTk.PhotoImage(img)

    def set_face(self, face):
        img = self.face_images[face]
        self.canvas.itemconfig(self.image_reference, image=img)


def main():
    root = tkinter.Tk()
    root.title('PySweeper')
    app = Application(master=root)
    app.mainloop()
    try:
        root.destroy()
    except tkinter.TclError as e:
        pass

if __name__ == "__main__":
    main()

