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

            ("gamedisplaymanager", "TileOpen"):       [self.tile_open],
            ("gamedisplaymanager", "TileToggleFlag"): [self.tile_toggle_flag],
            ("gamedisplaymanager", "TileChord"):      [self.tile_chord],
            ("gamedisplaymanager", "FaceClicked"):    [self.new_game],

            ("gamedisplaymanager", "TileDepress"):   [self.tile_depress],
            ("gamedisplaymanager", "TileUndepress"): [self.tile_undepress],

            ("pysweep", "<F2>"): [self.new_game],
            ("pysweep", "<F3>"): [self.new_game], # TODO: Create a UPK game

            ("pysweep", "AllModsLoaded"): [self.modsloaded],

            ("gamemode", "EnableGameMode"):  [self.onenable],
            ("gamemode", "DisableGameMode"): [self.ondisable],
        }

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name, priority=1, default=True)

        self.gamedisplay = self.pysweep.mods["GameDisplay"]

        self.rngmod = self.pysweep.mods["HashRandom"]
        self.rng = self.rngmod.get_rng()
        self.vid = [] # list of tuples. First element is string, remaining elements should be strings or numbers.
        self.hashvid = [] # same but contains what we'll put into the rng where sensitive numbers are rounded

        self.timermod = self.pysweep.mods["Timer"]
        self.timer = self.timermod.get_timer(self.timercallback, period=1, resolution=0.01)

        self.menuvar = tkinter.StringVar()
        self.menumod = self.pysweep.mods["Menu"]
        self.menu = tkinter.Menu(self.menumod.menubar, tearoff=0)
        self.menu.add_radiobutton(label="Playing Mode", variable=self.menuvar, command=self.playingmode)
        self.menu.add_radiobutton(label="Testing Mode", variable=self.menuvar, command=self.testingmode)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.set_timer(int(elapsed))
        if self.testing and elapsed > 10: # Testing mode :)
            self.lose_game(*self.mines[0])

    def onenable(self, hn, e):
        if e == game_mode_name:
            self.new_game(hn, e)

            self.menumod.add_menu("Mode", self.menu)
            self.menu.invoke(1)

    def ondisable(self, hn, e):
        if e == game_mode_name:
            self.timer.stop_timer()
            self.gamedisplay.reset_board()
            self.gamedisplay.set_timer(0)
            self.gamedisplay.set_mine_counter(0)
            self.gamedisplay.set_face_happy()

            self.menumod.remove_menu("Mode", self.menu)

    def playingmode(self):
        self.testing = False
    def testingmode(self):
        self.testing = True

    def new_game(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        width, height = self.gamedisplay.size

        self.notopened = []
        self.notdetermined = []
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
                self.notopened.append((row, col))
                self.notdetermined.append((row, col))

        self.timer.stop_timer()

        self.gamedisplay.reset_board()
        self.gamedisplay.set_face_happy()
        self.gamedisplay.set_timer(0)
        self.gamedisplay.set_mine_counter(self.num_mines)

        area = width*height
        if self.num_mines > area - 1:
            raise ValueException('More mines than spaces')

    def start_game(self, row, col):
        # First click at row, col
        width, height = self.gamedisplay.size

        self.state = "started"
        self.timer.start_timer()
        # for now let's just generate all mines on game start.
        while self.mines_generated < self.num_mines:
            row_ = int(random.random() * height)
            col_ = int(random.random() * width)
            if (row_, col_) not in self.mines and (row_, col_) != (row, col):
                self.mines.append((row_, col_))
                self.notmines.remove((row_, col_))
                self.mines_generated += 1
        # determine all the cells
        self.notdetermined = []
        for row_ in range(height):
            for col_ in range(width):
                self.determined.append((row_, col_))


    def lose_game(self, row, col):
        # Blast at row, col
        width, height = self.gamedisplay.size

        self.timer.stop_timer()
        # Display all mines
        for (minerow, minecol) in self.mines:
            if (minerow, minecol) not in self.flagged:
                self.gamedisplay.set_tile_mine(minerow, minecol)
        # Find wrong flags
        for (flagrow, flagcol) in self.flagged:
            if (flagrow, flagcol) not in self.mines:
                self.gamedisplay.set_tile_flag_wrong(flagrow, flagcol)
        self.gamedisplay.set_face_blast()
        self.gamedisplay.set_tile_blast(row, col)
        self.state = "ended"

    def win_game(self):
        # Opened all the tiles!
        width, height = self.gamedisplay.size

        self.timer.stop_timer()
        for (minerow, minecol) in self.mines:
            self.gamedisplay.set_tile_flag(minerow, minecol)
        self.gamedisplay.set_face_cool()
        self.state = "ended"

    def tile_depress(self, hn, e):
        if (not self.gamemodeselector.is_enabled(game_mode_name) or
                self.state == "ended"):
            return
        self.gamedisplay.set_tile_number(e.row, e.col, 0)
    def tile_undepress(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.set_tile_unopened(e.row, e.col)

    def tile_open(self, hn, e):
        width, height = self.gamedisplay.size
        row, col = e.row, e.col

        if (not self.gamemodeselector.is_enabled(game_mode_name) or
                self.state == "ended" or
                not (0 <= row < height and 0 <= col < width) or
                (row, col) in self.opened or (row, col) in self.flagged):
            return

        # FIRST CLICK SETUP
        if self.state == "notstarted":
            self.start_game(row, col)

        self.opened.append((row, col))
        self.notopened.remove((row, col))

        # Clicked a mine
        if (row, col) in self.mines:
            self.lose_game(row, col)
            return

        # Did not click mine. Calculate number
        number = self.num_mines_around(row, col)
        self.gamedisplay.set_tile_number(row, col, number)
        # If number is zero, open every tile around it
        if number == 0:
            for drow in range(-1, 2):
                for dcol in range(-1, 2):
                    e.row, e.col = row + drow, col + dcol
                    self.tile_open(hn, e)

        # Win condition
        if len(self.notopened) == len(self.mines):
            # we've opened everything :D (without blowing up)
            self.win_game()

    def num_mines_around(self, row, col):
        number = 0
        for (minerow, minecol) in self.mines:
            if abs(minerow - row) <= 1 and abs(minecol - col) <= 1:
                number += 1
        return number

    def num_flags_around(self, row, col):
        number = 0
        for (flagrow, flagcol) in self.flagged:
            if abs(flagrow - row) <= 1 and abs(flagcol - col) <= 1:
                number += 1
        return number

    def tile_toggle_flag(self, hn, e):
        width, height = self.gamedisplay.size
        row, col = e.row, e.col

        if (not self.gamemodeselector.is_enabled(game_mode_name) or
                self.state == "ended" or
                (row, col) in self.opened):
            return

        if (row, col) in self.flagged:
            self.flagged.remove((row, col))
            self.gamedisplay.set_tile_unopened(row, col)
        else:
            self.flagged.append((row, col))
            self.gamedisplay.set_tile_flag(row, col)

        self.gamedisplay.set_mine_counter(self.num_mines - len(self.flagged))

    def tile_chord(self, hn, e):
        width, height = self.gamedisplay.size
        row, col = e.row, e.col

        if (not self.gamemodeselector.is_enabled(game_mode_name) or
                self.state == "ended" or
                (row, col) not in self.opened):
            return

        squarenum = self.gamedisplay.get_tile_number(row, col)
        flagcount = self.num_flags_around(row, col)
        if flagcount == squarenum:
            # Square is fulfilled. Time to chord!
            for drow in range(-1, 2):
                for dcol in range(-1, 2):
                    e.row, e.col = row+drow, col+dcol
                    self.tile_open(hn, e) # tile_open knows not to open flags


    def on_mouse_move(self, hn, e):
        pass # TODO: This will feed into the rng!

mods = {"Minesweeper": Minesweeper}
