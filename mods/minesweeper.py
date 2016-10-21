import tkinter

import random

game_mode_name = "Minesweeper"

class Minesweeper:
    hooks = {}
    required_events = [
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
            ("clicker", "Move"): [self.on_mouse_move],

            ("gamedisplaymanager", "TileClicked"): [self.tile_clicked],
            ("gamedisplaymanager", "TileRightClicked"): [self.tile_right_clicked],
            ("gamedisplaymanager", "FaceClicked"): [self.new_game],

            ("pysweep", "<F2>"): [self.new_game],
            ("pysweep", "<F3>"): [self.new_game], # TODO: Create a UPK game

            ("pysweep", "AllModsLoaded"): [self.modsloaded],

            ("gamemode", "EnableGameMode"): [self.onenable],
        }

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
        self.timer = self.timermod.get_timer(self.timercallback, period=1, resolution=0.01)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.display.set_timer(int(elapsed))

    def onenable(self, hn, e):
        if e == game_mode_name:
            self.new_game(hn, e)

    def new_game(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        width, height = self.gamedisplaymanager.get_size()

        self.notopened = []
        self.notdetermined = []
        self.notmines = []
        self.opened = []
        self.determined = []
        self.mines = []
        self.num_mines = 99
        self.mines_generated = 0
        self.state = "notstarted"
        self.flagged = []
        # notstarted means before first click,
        # started means after the first click,
        # ended means the board was cleared or a mine was opened.

        # init arrays which are not supposed to start empty
        for row in range(height):
            for col in range(width):
                self.notmines.append((row, col))
                self.notopened.append((row, col))
                self.notdetermined.append((row, col))

        self.timer.stop_timer()

        self.gamedisplaymanager.reset_board()
        self.gamedisplaymanager.set_face_happy()
        self.gamedisplay.display.set_timer(0)
        self.gamedisplay.display.panel.mine_counter.set_value(self.num_mines)

        area = width*height
        if self.num_mines > area - 1:
            raise ValueException('More mines than spaces')

    def tile_clicked(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return

        if self.state == "ended":
            return

        width, height = self.gamedisplaymanager.get_size()

        row, col = e.row, e.col

        if not (0 <= row < height and 0 <= col < width):
            return

        if (row, col) in self.opened:
            return

        if (row, col) in self.flagged:
            return

        # FIRST CLICK SETUP
        if self.state == "notstarted":
            self.state = "started"
            self.timer.start_timer()
            # for now let's just generate all mines on game start.
            while self.mines_generated < self.num_mines:
                row_ = int(random.random() * height)
                col_ = int(random.random() * width)
                if (row_, col_) not in self.mines and (row_, col_) != (e.row, e.col):
                    self.mines.append((row_, col_))
                    self.notmines.remove((row_, col_))
                    self.mines_generated += 1
            # determine all the cells
            self.notdetermined = []
            for row_ in range(height):
                for col_ in range(width):
                    self.determined.append((row_, col_))

        self.opened.append((row, col))
        self.notopened.remove((row, col))
        if (row, col) in self.mines:
            # DEAD
            self.timer.stop_timer()
            for (minerow, minecol) in self.mines:
                if (minerow, minecol) not in self.flagged:
                    self.gamedisplaymanager.set_tile_mine(minerow, minecol)
            self.gamedisplaymanager.set_face_blast()
            self.gamedisplaymanager.set_tile_blast(row, col)
            self.state = "ended"
            return
        # NOT DEAD, calculate number
        number = 0
        for (minerow, minecol) in self.mines:
            if abs(minerow - row) <= 1 and abs(minecol - col) <= 1:
                number += 1
        self.gamedisplaymanager.set_tile_number(row, col, number)
        # If number is zero, click every tile around it
        if number == 0:
            for drow in range(-1, 2):
                for dcol in range(-1, 2):
                    e.row, e.col = row + drow, col + dcol
                    self.tile_clicked(hn, e)
        if len(self.notopened) == len(self.mines):
            # we've opened everything :D (without blowing up)
            self.timer.stop_timer()
            for (minerow, minecol) in self.mines:
                self.gamedisplaymanager.set_tile_flag(minerow, minecol)
            self.gamedisplaymanager.set_face_cool()
            self.state = "ended"

        # TODO: more logic needed lol
        # Done ish?

    def tile_right_clicked(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return

        width, height = self.gamedisplaymanager.get_size()

        row, col = e.row, e.col

        if (row, col) in self.opened:
            return

        if (row, col) in self.flagged:
            self.flagged.remove((row, col))
            self.gamedisplaymanager.set_tile_unopened(row, col)
        else:
            self.flagged.append((row, col))
            self.gamedisplaymanager.set_tile_flag(row, col)

        self.gamedisplay.display.panel.mine_counter.set_value(self.num_mines - len(self.flagged))

    def on_mouse_move(self, hn, e):
        pass # TODO: This will feed into the rng!

    def on_mouse_event(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplaymanager.handle_mouse_event(hn, e)

mods = {"Minesweeper": Minesweeper}
