import tkinter

import random

game_mode_name = "Speed Game"
class SpeedGame:
    hooks = {}
    required_events = [
        ("pysweep", "<ButtonPress-1>"),
        ("pysweep", "<B1-Motion>"),
        ("pysweep", "<ButtonRelease-1>"),

        ("face_button", "<ButtonPress-1>"),
        ("face_button", "<ButtonRelease-1>"),

        ("pysweep", "<F2>"),
        ("pysweep", "<F3>"),

        ("mine_counter", "<ButtonPress-1>"),
        ("timer", "<ButtonPress-1>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<ButtonPress-1>"):   [self.on_mouse_event],
            ("pysweep", "<B1-Motion>"):       [self.on_mouse_event],
            ("pysweep", "<ButtonRelease-1>"): [self.on_mouse_event],

            ("gamedisplaymanager", "TileClicked"): [self.tile_clicked],
            ("gamedisplaymanager", "FaceClicked"): [self.new_game],

            ("pysweep", "<F2>"): [self.new_game],
            ("pysweep", "<F3>"): [(lambda hn,e:self.reset_game())],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }
        self.temporarily_down = []
        self.speed_game_squares = []
        self.num_squares = 5

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

        self.gamedisplay = self.pysweep.mods["GameDisplay"]

        self.gamedisplaymanager = self.pysweep.mods["GameDisplayManager"]

        self.timermod = self.pysweep.mods["Timer"]
        self.timer = self.timermod.get_timer(self.timercallback, resolution=0.001)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.display.set_timer(int(elapsed*1000))

    def new_game(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        width, height = self.gamedisplay.size
        area = width*height
        if not 0 <= self.num_squares < area:
            self.num_squares = 0
        squares = []
        i = 0
        while i < self.num_squares:
            rand = random.randint(0, area-1)
            if rand not in squares:
                squares.append(rand)
                i += 1
        self.speed_game_original = squares[:]
        self.reset_game()

    def reset_game(self):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        width, height = self.gamedisplay.size
        area = width*height
        squares = self.speed_game_original[:]
        self.speed_game_squares = squares[:]
        for i in range(area):
            row = i//width
            col = i%width
            if i in squares:
                self.gamedisplaymanager.set_tile_unopened(row, col)
            else:
                self.gamedisplaymanager.set_tile_number(row, col, 0)
        self.gamedisplaymanager.update()
        self.gamedisplay.display.panel.face_button.set_face("happy")
        self.timer.start_timer()

    def tile_clicked(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return

        row, col = e.row, e.col

        board = self.gamedisplay.display.board
        width = board.board_width
        height = board.board_height
        if (0 <= col < width and 0 <= row < height):
            self.gamedisplaymanager.set_tile_number(row, col, 0)
            self.gamedisplaymanager.update()
            i = row*width + col
            if i in self.speed_game_squares:
                self.speed_game_squares.remove(i)
            if len(self.speed_game_squares) == 0:
                self.timer.stop_timer()
                self.gamedisplay.display.panel.face_button.set_face("cool")

    def on_mouse_event(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplaymanager.handle_mouse_event(hn, e)

mods = {"SpeedGame": SpeedGame}
