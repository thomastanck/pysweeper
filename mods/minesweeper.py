import tkinter

import random

game_mode_name = "Minesweeper"

class Minesweeper:
    hooks = {}
    required_events = [
        ("board", "<ButtonPress-1>"),
        ("board", "<B1-Motion>"),
        ("board", "<ButtonRelease-1>"),

        ("pysweep", "<Motion>"),

        ("face_button", "<ButtonPress-1>"),
        ("face_button", "<ButtonRelease-1>"),

        ("pysweep", "<F2>"),
        ("pysweep", "<F3>"),
    ]
    required_protocols = []

    # board events: to board manager
    # pysweep motion: record to vid file
    # gamedisplaymanager: when tile clicked, if it is not a mine, calculate cells that need to be determined. determine them, then reveal the cell that the player just clicked (calculate the number). the click goes in the vid file. if it is a mine, determine the rest of the board and show face blast and all that jazz.
    # face_button: depress when clicked. when released, start new game by setting state to notstarted, resetting determined cells and mines to empty lists (or the equivalent) then set whole board to unopened.
    # f2: same as above.
    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<ButtonPress-1>"):   [self.on_mouse_event],
            ("pysweep", "<B1-Motion>"):       [self.on_mouse_event],
            ("pysweep", "<ButtonRelease-1>"): [self.on_mouse_event],

            ("pysweep", "<Motion>"): [self.on_mouse_move],

            ("gamedisplaymanager", "TileClicked"): [self.tile_clicked],
            ("gamedisplaymanager", "FaceClicked"): [self.new_game],

            ("pysweep", "<F2>"): [self.new_game],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

        self.opened = []
        self.determined = []
        self.mines = []
        self.num_mines = 99
        self.state = "notstarted"
        # notstarted means before first click,
        # started means after the first click,
        # ended means the board was cleared or a mine was opened.

        print("##################################")
        print("#     MINESWEEPER NOT TESTED     #")
        print("##################################")

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

        self.gamedisplay = self.pysweep.mods["GameDisplay"]

        self.gamedisplaymanager = self.pysweep.mods["GameDisplayManager"]

        self.rngmod = self.pysweep.mods["HashRandom"]
        self.rng = self.rngmod.get_rng()
        self.vid = [] # list of tuples. First element is string, remaining elements should be strings or numbers.
        self.hashvid = [] # same but contains what we'll put into the rng where sensitive numbers are rounded

        self.timermod = self.pysweep.mods["Timer"]
        self.timer = self.timermod.get_timer(self.timercallback, resolution=0.001)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.display.set_timer(int(elapsed*1000))

    def onenable(self, hm, e):
        # TODO: implement enable/disable hooks in GameModeSelector
        self.new_game(hn, e)

    def new_game(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        width, height = self.gamedisplaymanager.get_size()
        self.gamedisplaymanager.reset_board()
        self.state = "notstarted"

        area = width*height
        if self.num_mines > area - 1:
            raise ValueException('More mines than spaces')

        self.opened = []
        self.determined = []
        self.mines = []

    def tile_clicked(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return

        width, height = self.gamedisplaymanager.get_size()

        if self.state == "notstarted":
            self.state = "started"
            # for now let's just generate all mines on game start.
            while len(self.mines) < self.num_mines:
                row = int(random.random() * height)
                col = int(random.random() * width)
                if (row, col) not in self.mines and (row, col) != (e.row, e.col):
                    self.mines.append((row, col))

        row, col = e.row, e.col

        if not (0 <= row < height and 0 <= col < width):
            return

        if (row, col) in self.opened:
            return
        self.opened.append((row, col))
        if (row, col) in self.mines:
            for (minerow, minecol) in self.mines:
                self.gamedisplaymanager.set_tile_mine(minerow, minecol)
            self.gamedisplaymanager.set_face_blast()
            self.gamedisplaymanager.set_tile_blast(row, col)
            return
        number = 0
        for (minerow, minecol) in self.mines:
            if abs(minerow - row) <= 1 and abs(minecol - col) <= 1:
                number += 1
        self.gamedisplaymanager.set_tile_number(row, col, number)
        if number == 0:
            for drow in range(-1, 2):
                for dcol in range(-1, 2):
                    e.row, e.col = row + drow, col + dcol
                    self.tile_clicked(hn, e)

        # TODO: more logic needed lol
        # Done ish?

    def on_mouse_move(self, hn, e):
        pass # TODO: This will feed into the rng!

    def on_mouse_event(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplaymanager.handle_mouse_event(hn, e)

mods = {"Minesweeper": Minesweeper}
