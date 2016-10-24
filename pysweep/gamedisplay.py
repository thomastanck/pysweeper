import tkinter
from PIL import Image, ImageTk
import pysweep

image_dir = "images"

class GameDisplayEvent:
    __isfrozen = False
    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError( "%r is a frozen class, cannot set %s" % (self, key))
        object.__setattr__(self, key, value)

    def __init__(self, event=None, time=0, arg="", row=0, col=0):
        self.event = event
        self.time = time
        self.arg = arg
        self.row = row
        self.col = col
        self.__isfrozen = True

class GameDisplayWrapper:
    hooks = {}
    required_events = []
    required_protocols = []

    # WIDGET BINDING STUFF
    ######################
    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.display = GameDisplay(master, self.pysweep, 30, 16) # default size is expert

        self.master.withdraw()
        self.display.pack()
        self.center_window()
        self.master.deiconify()

        self.current_face = "happy"

    # GENERAL PROPERTIES
    ####################
    @property
    def board_size(self):
        return (self.board.board_width, self.board.board_height)
    @property
    def tile_size(self):
        return self.board.tile_size



    # WIDGET PROPERTIES
    ###################
    @property
    def board(self):
        return self.display.board
    @property
    def panel(self):
        return self.display.panel
    @property
    def mine_counter(self):
        return self.display.panel.mine_counter
    @property
    def face_button(self):
        return self.display.panel.face_button
    @property
    def timer(self):
        return self.display.panel.timer


    # GENERAL DISPLAY STUFF
    #######################
    def set_size(self, width, height):
        # Warning, completely kills GameDisplay. You'll have to give it new data after this
        self.display.pack_forget()
        self.display.destroy()
        self.display = GameDisplay(self.master, self.pysweep, width, height)

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


    # SENDING EVENTS
    ################
    def send_event(self, e):
        self.pysweep.handle_event(("gamedisplay", e.event), e)


    # BOARD SETTERS AND GETTERS
    ###########################

    # Tile setters
    def set_tile_mine(self, row, col):
        self.set_tile_other(row, col, "mine")
    def set_tile_blast(self, row, col):
        self.set_tile_other(row, col, "blast")
    def set_tile_flag(self, row, col):
        self.set_tile_other(row, col, "flag")
    def set_tile_flag_wrong(self, row, col):
        self.set_tile_other(row, col, "flag_wrong")
    def set_tile_unopened(self, row, col):
        self.set_tile_other(row, col, "unopened")

    def set_tile_other(self, row, col, tile_type):
        self.send_event(GameDisplayEvent("TileOther", pysweep.time(), tile_type, row, col))
        self.set_tile(row, col, tile_type)
    def set_tile_number(self, row, col, number):
        # number: 0..8
        if type(number) == int and 0 <= number and number < 9:
            self.send_event(GameDisplayEvent("TileNumber", pysweep.time(), number, row, col))
            self.set_tile(row, col, "tile_{}".format(number))
        else:
            raise ValueError('Tile number {} does not exist'.format(number))

    def set_tile(self, row, col, tile_type):
        self.board.draw_tile(row, col, tile_type)

    # Tile getters
    def is_tile_mine(self, row, col):
        return self.get_tile_type(row, col) == "mine"
    def is_tile_blast(self, row, col):
        return self.get_tile_type(row, col) == "blast"
    def is_tile_flag(self, row, col):
        return self.get_tile_type(row, col) == "flag"
    def is_tile_flag_wrong(self, row, col):
        return self.get_tile_type(row, col) == "flag_wrong"
    def is_tile_unopened(self, row, col):
        return self.get_tile_type(row, col) == "unopened"
    def is_tile_number(self, row, col):
        try:
            return 0 <= int(self.get_tile_type(row, col)[-1:]) <= 8
        except:
            return False
    def get_tile_number(self, row, col):
        return int(self.get_tile_type(row, col)[-1:]) # get the last char and convert to int
    def get_tile_type(self, row, col):
        return self.board.get_tile_type(row, col)

    # Reset board (set all to unopened)
    def reset_board(self):
        width, height = self.board_size

        for row in range(height):
            for col in range(width):
                self.set_tile_unopened(row, col)


    # OTHER SETTERS AND GETTERS
    ###########################

    # Face button setters
    def set_face_happy(self):
        self.set_face("happy")
    def set_face_pressed(self):
        self.set_face("pressed")
    def set_face_blast(self):
        self.set_face("blast")
    def set_face_cool(self):
        self.set_face("cool")
    def set_face_nervous(self):
        self.set_face("nervous")
    def set_face(self, face):
        if self.current_face != face:
            self.current_face = face
            self.send_event(GameDisplayEvent("Face", pysweep.time(), face))
            self.face_button.set_face(face)

    # Counters
    def set_timer(self, t):
        self.send_event(GameDisplayEvent("Timer", pysweep.time(), t))
        self.timer.set_value(t)

    def set_mine_counter(self, t):
        self.send_event(GameDisplayEvent("MineCounter", pysweep.time(), t))
        self.mine_counter.set_value(t)

class BorderCanvas(tkinter.Canvas):
    def __init__(self, master, image, copies=1, direction='h'):
        """
        direction is the direction the image is copied, either
        h for horizontal, or v for vertical
        """
        self.original_image = image
        self.copies = copies
        self.direction = 'v' if direction.lower() == 'v' else 'h'

        width, height = self.canvas_size

        super().__init__(master, width=width, height=height,
                         highlightthickness=0)

        self.image_ref = self.create_image((0, 0), anchor='nw')
        self.build_image()

    def build_image(self):
        new_image = Image.new(size=self.canvas_size, mode='RGB')
        width, height = self.original_image.size
        for col in range(self.grid_size[0]):
            for row in range(self.grid_size[1]):
                new_image.paste(self.original_image, box=(col*width, row*height))
        self.image = ImageTk.PhotoImage(new_image)
        self.itemconfig(self.image_ref, image=self.image)

    def resize(self, copies):
        self.copies = copies
        self.build_image()
        width, height = self.canvas_size
        self.config(width=width, height=height)


    @property
    def canvas_size(self):
        w_factor, h_factor = self.grid_size
        orig_size = self.original_image.size
        w, h = orig_size[0]*w_factor, orig_size[1]*h_factor
        return (w, h)

    @property
    def grid_size(self):
        if self.direction.lower() == 'v':
            return (1, self.copies)
        else:
            return (self.copies, 1)


class GameDisplay(tkinter.Frame):
    border_images = {}
    def create_widgets(self):
        # the main playing area:
        self.board = Board(self, self.board_width, self.board_height)
        tile_size = self.board.tile_size
        board_canvas_w, board_canvas_h = self.board.canvas_size

        # Grid row 0: Top border
        border_images = self.border_images
        grid_row = 0
        self.border_top_left = BorderCanvas(self, border_images['top_l'])
        self.border_top = BorderCanvas(self, border_images['top'],
                                       board_canvas_w, 'h')
        self.border_top_right = BorderCanvas(self, border_images['top_r'])
        for i, name in enumerate(('_left', '', '_right')):
            getattr(self, "border_top{}".format(name)).grid(row=grid_row, column=i)

        # Grid row 1: Left and right borders, Panel
        grid_row = 1
        self.border_panel_left = BorderCanvas(
            self, border_images['panel_l'], 26, 'v')
        self.panel = Panel(self, width=board_canvas_w)
        self.border_panel_right = BorderCanvas(
            self, border_images['panel_r'], 26, 'v')
        self.border_panel_left.grid(row=grid_row, column=0)
        self.panel.grid(row=grid_row, column=1, sticky="nesw")
        self.border_panel_right.grid(row=grid_row, column=2)

        # Grid row 2: Middle divider between Panel and Board
        grid_row = 2
        self.border_mid_left = BorderCanvas(self, border_images['mid_l'])
        self.border_mid = BorderCanvas(self, border_images['mid'],
                                     board_canvas_w, 'h')
        self.border_mid_right = BorderCanvas(self, border_images['mid_r'])
        for i, name in enumerate(('_left', '', '_right')):
            getattr(self, "border_mid{}".format(name)).grid(row=grid_row, column=i)

        # Grid row 3: Left and right board boarder, Board
        grid_row = 3
        self.border_left = BorderCanvas(self, border_images['l'],
                                        board_canvas_h, 'v')
        self.border_right = BorderCanvas(self, border_images['r'],
                                         board_canvas_h, 'v')
        self.border_left.grid(row=grid_row, column=0)
        self.board.grid(row=grid_row, column=1)
        self.border_right.grid(row=grid_row, column=2)

        # Grid row 4: Bottom board border
        grid_row = 4
        self.border_bot_left = BorderCanvas(self, border_images['bot_l'])
        self.border_bot = BorderCanvas(self, border_images['bot'],
                                       board_canvas_w, 'h')
        self.border_bot_right = BorderCanvas(self, border_images['bot_r'])
        for i, name in enumerate(('_left', '', '_right')):
            getattr(self, "border_bot{}".format(name)).grid(row=grid_row, column=i)

    def load_border_images(self):
        for key in ('l', 'r', 'top', 'mid', 'top_l', 'top_r', 'panel_l',
                    'panel_r', 'mid_l', 'mid_r', 'bot', 'bot_l', 'bot_r'):
            img = Image.open("{}/border_{}.png".format(image_dir, key))
            self.border_images[key] = img


    def __init__(self, master, pysweep, board_width=16, board_height=16):
        self.pysweep = pysweep
        self.board_width = board_width
        self.board_height = board_height
        super().__init__(master)
        self.load_border_images()
        self.create_widgets()
        board_size = self.board.canvas_size
        self.config(width=board_size[0], height=board_size[1])



class Tile:
    def __init__(self, row, column, state=None):
        self.row = row
        self.column = column
        self.state = state


class Board(tkinter.Frame):
    def __init__(self, master, width, height):
        super().__init__(master)
        self.board_width = width
        self.board_height = height
        self.tile_size = None
        self.update_canvas_queued = False
        self.load_tiles()
        w, h = self.canvas_size
        self.canvas = tkinter.Canvas(self, width=w, height=h,
                                     highlightthickness=0)
        self.canvas_img_ref = self.canvas.create_image((0,0), anchor="nw")
        self.init_canvas()

        self.canvas.pack()

    def resize(self, width, height):
        self.board_width = width
        self.board_height = height
        self.canvas.config(width=self.canvas_size[0], height=self.canvas_size[1])
        self.init_canvas()

    def init_canvas(self):
        self.canvas_rgb = Image.new(size=self.canvas_size, mode="RGB")
        self.canvas_img = ImageTk.PhotoImage(self.canvas_rgb)
        self.canvas.itemconfig(self.canvas_img_ref, image=self.canvas_img)
        for col in range(self.board_width):
            for row in range(self.board_height):
                self.draw_tile(row, col, "unopened")


    def load_tiles(self):
        tile_images = {}
        tile_names = ["tile_{}".format(i) for i in range(9)]
        for key in tile_names + ["unopened", "flag", "blast", "flag_wrong", "mine"]:
            img = Image.open("{}/{}.png".format(image_dir, key))
            if self.tile_size is None:
                self.tile_size = img.size
            else:
                try:
                    assert self.tile_size == img.size
                except AssertionError as e:
                    e.args += (' '.join(("All tile images must be of same size.",
                                         "\"{}/{}.png\"".format(image_dir, key),
                                        "has size ({}, {}).".format(*img.size))),
                    )
                    raise e
            tile_images[key] = img
        self.tile_images = tile_images

        width = self.board_width
        height = self.board_height
        tiles = [[Tile(r, c, None) for c in range(width)]
                 for r in range(height)]
        self.tiles = tiles

    def get_tile_type(self, i, j):
        return self.tiles[i][j].state

    def draw_tile(self, row, col, state):
        tile = self.tiles[row][col]
        if tile.state == state:
            return False
        tile.state = state
        tile_img = self.tile_images[state]
        tile_w, tile_h = self.tile_size
        self.canvas_rgb.paste(tile_img, box=(col*tile_w, row*tile_h))
        if not self.update_canvas_queued:
            self.update_canvas_queued = True
            self.master.after(0, self.update_canvas)
        return True

    def update_canvas(self):
        self.update_canvas_queued = False
        self.canvas_img.paste(self.canvas_rgb)

    def reset_board(self):
        width = self.board_width
        height = self.board_height
        for i in range(height):
            for j in range(width):
                self.draw_tile(i, j, "unopened")

    @property
    def canvas_size(self):
        return (self.tile_size[0]*self.board_width,
                self.tile_size[1]*self.board_height)



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
                img = Image.open("{}/counter_border_{}.png".format(image_dir, key))
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
                img = Image.open("{}/counter_{}.png".format(image_dir, i))
                Digit.digits[i] = ImageTk.PhotoImage(img)

    def set_value(self, n):
        self.mastercanvas.itemconfig(self.image_reference, image=Digit.digits[n])

class Panel(tkinter.Frame):
    def __init__(self, master, width):
        super().__init__(master, width=width, height=26)
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
        for key in ["happy", "pressed", "blast", "cool", "nervous"]:
            img = Image.open("{}/face_{}.png".format(image_dir, key))
            self.face_images[key] = ImageTk.PhotoImage(img)

    def set_face(self, face):
        img = self.face_images[face]
        self.canvas.itemconfig(self.image_reference, image=img)
