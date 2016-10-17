import tkinter
from PIL import Image, ImageTk
import time

class GameDisplayWrapper:
    hooks = {}
    bindable_widgets = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.size = (30, 16) # Default size is expert
        self.display = GameDisplay(master, self.pysweep3, *self.size)

        self.bindable_widgets = {
            "board":        {"bindevent": lambda e_n,widget_name="board":        self.bind_tkinter_event(e_n, widget_name)},
            "panel":        {"bindevent": lambda e_n,widget_name="panel":        self.bind_tkinter_event(e_n, widget_name)},
            "mine_counter": {"bindevent": lambda e_n,widget_name="mine_counter": self.bind_tkinter_event(e_n, widget_name)},
            "face_button":  {"bindevent": lambda e_n,widget_name="face_button":  self.bind_tkinter_event(e_n, widget_name)},
            "timer":        {"bindevent": lambda e_n,widget_name="timer":        self.bind_tkinter_event(e_n, widget_name)},
        }
        self.bind_events = []

        self.center_window()
        self.master.withdraw()
        self.display.pack()
        self.master.deiconify()

    def rebind_tkinter_events(self):
        widgets = {
            "board":        self.display.board.canvas,
            "panel":        self.display.panel,
            "mine_counter": self.display.panel.mine_counter.canvas,
            "face_button":  self.display.panel.face_button.canvas,
            "timer":        self.display.panel.timer.canvas,
        }
        for event_name, widget_name in self.bind_events:
            hook = (widget_name, event_name)
            widgets[widget_name].bind(event_name, lambda e,hook=hook: self.handle_event(hook, e))

    def bind_tkinter_event(self, event_name, widget_name):
        widgets = {
            "board":        self.display.board.canvas,
            "panel":        self.display.panel,
            "mine_counter": self.display.panel.mine_counter.canvas,
            "face_button":  self.display.panel.face_button.canvas,
            "timer":        self.display.panel.timer.canvas,
        }
        if (event_name, widget_name) not in self.bind_events:
            hook = (widget_name, event_name)
            widgets[widget_name].bind(event_name, lambda e,hook=hook: self.handle_event(hook, e))
            self.bind_events.append((event_name, widget_name))

    def handle_event(self, hook, e):
        e.row = e.y//16
        e.col = e.x//16
        self.pysweep3.handle_event(hook, e)

    def set_size(self, width, height):
        # Warning, completely kills GameDisplay. You'll have to give it new data after this
        self.size = (width, height)
        self.display.pack_forget()
        self.display.destroy()
        self.display = GameDisplay(self.master, self.pysweep3, *self.size)
        self.rebind_tkinter_events()

    def center_window(self):
        self.display.update_idletasks()
        h = self.display.winfo_reqheight()
        w = self.display.winfo_reqwidth()

        # get screen width and height
        ws = self.master.winfo_screenwidth() # width of the screen
        hs = self.master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        self.master.geometry('+%d+%d' % (x, y))

class GameDisplay(tkinter.Frame):
    border_images = {}
    def create_widgets(self):
        # Grid row 0: Top border
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

        # Grid row 1: Left and right borders, Panel
        grid_row = 1
        self.border_panel_left = tkinter.Canvas(self, width=12, height=26,
                                             highlightthickness=0)
        self.panel = Panel(self, board_width=self.board_width)
        self.border_panel_right = tkinter.Canvas(self, width=12, height=26,
                                                 highlightthickness=0)
        self.border_panel_left.grid(row=grid_row, column=0)
        self.panel.grid(row=grid_row, column=1, sticky="nesw")
        self.border_panel_right.grid(row=grid_row, column=2)

        # Grid row 2: Middle divider between Panel and Board
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

        # Set up Board widget
        self.border_left = tkinter.Canvas(self, width=12,
                                          height=16*self.board_height)
        self.border_left.config(highlightthickness=0)
        self.board = Board(self, self.board_width, self.board_height)
        self.border_right = tkinter.Canvas(self, width=12,
                                           height=16*self.board_height)
        self.border_right.config(highlightthickness=0)

        # Grid row 3: Left and right board boarder, Board
        grid_row = 3
        self.border_left.grid(row=grid_row, column=0)
        self.board.grid(row=grid_row, column=1)
        self.border_right.grid(row=grid_row, column=2)

        # Grid row 4: Bottom board border
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


    def __init__(self, master, pysweep3, board_width=16, board_height=16):
        self.pysweep3 = pysweep3
        self.board_width = board_width
        self.board_height = board_height
        super().__init__(master, width=board_width*16+24, height=board_height*16+67)
        self.create_widgets()

    def set_timer(self, t):
        self.panel.timer.set_value(t)



class Tile:
    tile_images = {}
    def __init__(self, tile_id, state=None):
        self.tile_id = tile_id
        self.state = state


class Board(tkinter.Frame):
    def load_tiles(self):
        tile_images = {}
        tile_names = ["tile_{}".format(i) for i in range(9)]
        for key in tile_names + ["unopened", "flag", "blast", "flag_wrong", "mine"]:
            img = Image.open("images/{}.png".format(key))
            tile_images[key] = ImageTk.PhotoImage(img)
        self.tile_images = tile_images

        width = self.board_width
        height = self.board_height
        tiles = [[Tile(self.canvas.create_image((i*16,j*16), anchor="nw"))
                  for i in range(width)] for j in range(height)]
        self.tiles = tiles

    def get_tile_type(self, i, j):
        return self.tiles[i][j].state

    def set_tile(self, i, j, tile_type):
        tile = self.tiles[i][j]
        tile_id = self.tiles[i][j].tile_id
        if tile_type != tile.state:
            self.canvas.itemconfig(tile_id, image=self.tile_images[tile_type])
            tile.state = tile_type

    def reset_board(self):
        width = self.board_width
        height = self.board_height
        for i in range(height):
            for j in range(width):
                self.set_tile(i, j, "unopened")

    def __init__(self, master, width, height):
        super().__init__(master)
        self.board_width = width
        self.board_height = height
        self.canvas = tkinter.Canvas(self, width=16*width, height=16*height,
                                     highlightthickness=0)
        self.canvas.pack()
        self.load_tiles()
        for i in range(width):
            for j in range(height):
                self.set_tile(j, i, "unopened")

class Counter(tkinter.Frame):
    border_images = {}
    def create_widgets(self):
        self.digits = []
        display_width = self.display_width

        # Digits canvas. I put them all in the same canvas so we can bind
        # events to this canvas rather than many events to each individual digit.
        # Another way would be to use bind tags so we can listen to events from
        # the parent container (Counter), but it doesn't fit in nicely with
        # the current events system.
        self.canvas = tkinter.Canvas(self, width=13*display_width, height=23,
                         highlightthickness=0)
        for i in range(display_width):
            digit = Digit(self.canvas, i)
            self.digits.append(digit)
        self.canvas.grid(row=1,column=1,columnspan=display_width)

        # Left border
        self.border_left = tkinter.Canvas(self, width=1, height=25,
                                          highlightthickness=0)
        self.border_left.create_image((0,0), anchor='nw',
                                      image=self.border_images['l'])
        # Top border
        self.border_top = tkinter.Canvas(self, width=13*display_width,
                                         height=1, highlightthickness=0)
        for i in range(display_width):
            self.border_top.create_image((13*i,0), anchor='nw',
                                         image=self.border_images['t'])
        # Bottom border
        self.border_bot = tkinter.Canvas(self, width=13*display_width,
                                         height=1, highlightthickness=0)
        for i in range(display_width):
            self.border_bot.create_image((13*i,0), anchor='nw',
                                         image=self.border_images['b'])
        # Right border
        self.border_right = tkinter.Canvas(self, width=1, height=25,
                                           highlightthickness=0)
        self.border_right.create_image((0,0), anchor='nw',
                                       image=self.border_images['r'])

        # Grid the borders in
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


class Digit:
    digits = {}
    def __init__(self, mastercanvas, i):
        self.mastercanvas = mastercanvas
        self.i = i
        self.init_digits()
        self.image_reference = self.mastercanvas.create_image((i*13, 0), anchor='nw')
        self.set_value(0)

    def init_digits(self):
        if not Digit.digits:
            for i in list(range(10)) + ['-', 'off']:
                img = Image.open("images/counter_{}.png".format(i))
                Digit.digits[i] = ImageTk.PhotoImage(img)

    def set_value(self, n):
        self.mastercanvas.itemconfig(self.image_reference, image=Digit.digits[n])

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

mods = {"GameDisplay": GameDisplayWrapper}
