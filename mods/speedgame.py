import tkinter

import random

class SpeedGame:
    game_mode_name = "Speed Game"
    hooks = {}
    required_events = [
        ("board", "<ButtonPress-1>"),
        ("board", "<B1-Motion>"),
        ("board", "<ButtonRelease-1>"),

        ("face_button", "<ButtonPress-1>"),
        ("face_button", "<ButtonRelease-1>"),

        ("pysweep3", "<F2>"),
        ("pysweep3", "<F3>"),

        ("mine_counter", "<ButtonPress-1>"),
        ("timer", "<ButtonPress-1>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            ("board", "<ButtonPress-1>"):   [self.onpress],
            ("board", "<B1-Motion>"):       [self.onmove],
            ("board", "<ButtonRelease-1>"): [self.onrelease],

            ("face_button", "<ButtonPress-1>"):   [self.press_smiley],
            ("face_button", "<ButtonRelease-1>"): [self.new_game],

            ("pysweep3", "<F2>"): [self.new_game],
            ("pysweep3", "<F3>"): [(lambda hn,e:self.reset_game())],

            ("pysweep3", "AllModsLoaded"): [self.modsloaded],
        }
        self.temporarily_down = []
        self.speed_game_squares = []
        self.num_squares = 5

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep3.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(SpeedGame.game_mode_name)

        self.gamedisplay = self.pysweep3.mods["GameDisplay"]

        self.timermod = self.pysweep3.mods["Timer"]
        self.timer = self.timermod.get_timer(self.timercallback, resolution=0.001)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.display.set_timer(int(elapsed*1000))

    def press_smiley(self, hn, e):
        if not self.gamemodeselector.is_enabled(SpeedGame.game_mode_name):
            return
        self.gamedisplay.display.panel.face_button.set_face("pressed")

    def new_game(self, hn, e):
        if not self.gamemodeselector.is_enabled(SpeedGame.game_mode_name):
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
        if not self.gamemodeselector.is_enabled(SpeedGame.game_mode_name):
            return
        width, height = self.gamedisplay.size
        area = width*height
        squares = self.speed_game_original[:]
        self.speed_game_squares = squares[:]
        for i in range(area):
            row = i//width
            col = i%width
            tile = "unopened" if i in squares else "tile_0"
            self.set_tile(row, col, tile)
        self.gamedisplay.display.panel.face_button.set_face("happy")
        self.timer.start_timer()

    def onpress(self, hn, e):
        if not self.gamemodeselector.is_enabled(SpeedGame.game_mode_name):
            return
        board = self.gamedisplay.display.board

        col = e.col
        row = e.row
        width, height = board.board_width, board.board_height
        if not (0 <= col < width and 0 <= row < height):
            # i.e., we've moved off the board
            self.reset_depressed()
        else:
            self.reset_depressed(row, col)
            if self.get_tile_type(row, col) == "unopened":
                self.temporarily_down.append((row, col))
                self.set_tile(row, col, "tile_0")

    def onmove(self, hn, e):
        if not self.gamemodeselector.is_enabled(SpeedGame.game_mode_name):
            return
        self.onpress(hn, e)

    def onrelease(self, hn, e):
        if not self.gamemodeselector.is_enabled(SpeedGame.game_mode_name):
            return
        board = self.gamedisplay.display.board

        col = e.col
        row = e.row
        if (col, row) in self.temporarily_down:
            self.temporarily_down.remove((col,row))
        self.reset_depressed()
        width = board.board_width
        height = board.board_height
        if (0 <= col < width and 0 <= row < height):
            self.set_tile(row, col, "tile_0")
            i = row*width + col
            if i in self.speed_game_squares:
                self.speed_game_squares.remove(i)
            if len(self.speed_game_squares) == 0:
                self.timer.stop_timer()
                self.gamedisplay.display.panel.face_button.set_face("cool")

    def get_tile_type(self, i, j):
        board = self.gamedisplay.display.board
        return board.get_tile_type(i, j)

    def set_tile(self, i, j, tile_type):
        board = self.gamedisplay.display.board
        board.set_tile(i, j, tile_type)

    def reset_depressed(self, avoid_x=-1, avoid_y=-1):
        add_back = (avoid_x, avoid_y) in self.temporarily_down
        if add_back:
            self.temporarily_down.remove((avoid_x, avoid_y))
        while self.temporarily_down:
            x, y = self.temporarily_down.pop()
            self.set_tile(x, y, "unopened")
        if add_back:
            self.temporarily_down.append((avoid_x, avoid_y))

mods = {"SpeedGame": SpeedGame}
