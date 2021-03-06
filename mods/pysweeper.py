import tkinter
import tkinter.filedialog

from pysweep.util import own_game_mode, BoardClick
from pysweep import HashRandom, Timer, Menu
import pysweep

import math
import random

# Decorator that makes the function only do stuff if the game is not "ended"
def notended(f):
    def wrapper(self, hn, e):
        if self.state != "ended":
            return f(self, hn, e)
        else:
            return
    return wrapper

# Decorator that makes the function only do stuff if the tile in
# the event is in bounds.
def checkbounds(f):
    def wrapper(self, hn, e):
        width, height = self.gamedisplay.board_size
        if (0 <= e.row < height and 0 <= e.col < width):
            return f(self, hn, e)
        else:
            return
    return wrapper

# Decorator that makes the function only do stuff if the tile in
# the event is not yet opened/flagged/already opened
def notopened(f):
    def wrapper(self, hn, e):
        if (e.row, e.col) not in self.opened:
            return f(self, hn, e)
        else:
            return
    return wrapper
def notflagged(f):
    def wrapper(self, hn, e):
        if (e.row, e.col) not in self.flagged:
            return f(self, hn, e)
        else:
            return
    return wrapper
def opened(f):
    def wrapper(self, hn, e):
        if (e.row, e.col) in self.opened:
            return f(self, hn, e)
        else:
            return
    return wrapper

class PySweeper:
    game_mode_name = "PySweeper"
    hooks = {}
    required_events = [
        ("pysweep", "<F2>"),
        ("pysweep", "<F3>"),
    ]
    required_protocols = []

    rng_class = HashRandom
    is_default_mode = True

    # board events: to board manager
    # pysweep motion: record to vid file
    # gamedisplaymanager: when tile clicked, if it is not a mine, calculate cells that need to be determined. determine them, then reveal the cell that the player just clicked (calculate the number). the click goes in the vid file. if it is a mine, determine the rest of the board and show face blast and all that jazz.
    # face_button: depress when clicked. when released, start new game by setting state to notstarted, resetting determined cells and mines to empty lists (or the equivalent) then set whole board to unopened.
    # f2: same as above.
    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("clicker", "M"):  [self.on_mouse_move],

            ("gamedisplaymanager", "TileOpen"):       [self.tile_open],
            ("gamedisplaymanager", "TileToggleFlag"): [self.tile_toggle_flag],
            ("gamedisplaymanager", "TileChord"):      [self.tile_chord],
            ("gamedisplaymanager", "FaceClicked"):    [self.new_game],

            ("gamedisplaymanager", "TileDepress"):   [self.tile_depress],
            ("gamedisplaymanager", "TileUndepress"): [self.tile_undepress],
            ("gamedisplaymanager", "FaceDepress"):   [self.face_depress],
            ("gamedisplaymanager", "FaceUndepress"): [self.face_undepress],

            ("pysweep", "<F2>"): [self.new_game],
            ("pysweep", "<F3>"): [self.save_vid], # TODO: Create a UPK game. for now use it to print the video file :>

            ("pysweep", "AllModsLoaded"): [self.modsloaded],

            ("gamemode", "EnableGameMode"):  [self.onenable],
            ("gamemode", "DisableGameMode"): [self.ondisable],
        }

        self.prev_pos = (0, 0)

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(self.game_mode_name,
                                                 priority=0, default=self.is_default_mode)

        self.gamedisplay = self.pysweep.gamedisplay

        self.vidmod = self.pysweep.mods["VideoFile"]
        self.vid = self.vidmod.new_video_file(self.gamedisplay, self.game_mode_name, "Expert")

        self.timer = Timer(self.master, self.timercallback, period=1, resolution=0.01)

        self.menuvar = tkinter.StringVar()
        self.menu = tkinter.Menu(Menu.menubar, tearoff=0)
        self.menu.add_radiobutton(label="Playing Mode", variable=self.menuvar, command=self.playingmode)
        self.menu.add_radiobutton(label="Testing Mode", variable=self.menuvar, command=self.testingmode)

    @own_game_mode
    def save_vid(self, hn, e):
        f = tkinter.filedialog.asksaveasfile(mode='wb', defaultextension='.pyvf')
        f.write(self.vid.vidbytes)
        f.close()

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.set_timer(math.ceil(elapsed/1000))
        if self.testing and elapsed > 10*1000: # Testing mode :)
            self.lose_game(*self.mines[0])

    def _add_seed(self, seed):
        self.vid.add_command(["ADDSEED", repr(seed)])
        self.rng.update(repr(seed))

    @own_game_mode
    def onenable(self, hn, e):
        self.new_game(hn, e)

        Menu.add_menu("Mode", self.menu)
        self.menu.invoke(1)

    @own_game_mode
    def ondisable(self, hn, e):
        self.timer.stop_timer()
        self.gamedisplay.reset_board()
        self.gamedisplay.set_timer(0)
        self.gamedisplay.set_mine_counter(0)
        self.gamedisplay.set_face_happy()

        Menu.remove_menu("Mode", self.menu)

    def playingmode(self):
        self.testing = False
    def testingmode(self):
        self.testing = True

    @own_game_mode
    def on_mouse_move(self, hn, e_):
        e_.x = e_.x_root - self.gamedisplay.board.winfo_rootx()
        e_.y = e_.y_root - self.gamedisplay.board.winfo_rooty()
        e_.widget = self.gamedisplay.board
        e = BoardClick()
        e.fromClickerEvent(e_)
        if (e.row, e.col) != self.prev_pos:
            self.prev_pos = e.row, e.col
            self._add_seed(["MOVE", e.time//1000, e.row, e.col])

    @own_game_mode
    def new_game(self, hn, e):
        width, height = self.gamedisplay.board_size

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

        self.rng = self.rng_class()

        self.vidmod.del_video_file(self.vid)
        self.vid = self.vidmod.new_video_file(self.gamedisplay, self.game_mode_name, "Expert")
        self._add_seed(["SECONDS", pysweep.seconds()])
        self.vid.add_command(["NUMMINES", self.num_mines])
        self._add_seed(["NUMMINES", self.num_mines])
        self.vid.start_after_display_change()

    def start_game(self, row, col):
        # First click at row, col
        width, height = self.gamedisplay.board_size

        self.state = "started"
        self.timer.start_timer()
        self.vid.add_command(["STARTGAME", self.timer.start_time])
        self.vid.add_command(["SECONDS", self.timer.start_time//1000])
        self._add_seed(["SECONDS", self.timer.start_time//1000])
        # Just set the current cell to determined so no mines can be generated there,
        # then let the rest of the click handler do the job
        self.determined.append((row, col))
        self.notdetermined.remove((row, col))
        self.vid.add_command(["GENERATE", self.timer.start_time, row, col, False])
        self._add_seed(["GENERATE", self.timer.start_time//1000, row, col, False])

    def lose_game(self, row, col):
        # Blast at row, col
        width, height = self.gamedisplay.board_size

        self.timer.stop_timer()

        self.vid.add_command(["LOSE", self.timer.stop_time])
        self._add_seed(["LOSE", self.timer.stop_time//1000])

        # Determine all tiles
        self.determine_all_tiles()
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

        self.vid.stop()

    def win_game(self):
        # Opened all the tiles!
        width, height = self.gamedisplay.board_size

        self.timer.stop_timer()

        self.vid.add_command(["WIN", self.timer.stop_time])
        self._add_seed(["WIN", self.timer.stop_time//1000])

        # Determine all tiles just in case there was a huge chunk of
        # undetermined but guaranteed mines in a corner
        self.determine_all_tiles()
        for (minerow, minecol) in self.mines:
            self.gamedisplay.set_tile_flag(minerow, minecol)
        self.gamedisplay.set_face_cool()
        self.state = "ended"

        self.vid.stop()

    @own_game_mode
    @notended
    def tile_depress(self, hn, e):
        self.gamedisplay.set_tile_number(e.row, e.col, 0)
        self.gamedisplay.set_face_nervous()
    @own_game_mode
    def tile_undepress(self, hn, e):
        self.gamedisplay.set_tile_unopened(e.row, e.col)
        self.gamedisplay.set_face_happy()
    @own_game_mode
    def face_depress(self, hn, e):
        self.gamedisplay.set_face_pressed()
    @own_game_mode
    def face_undepress(self, hn, e):
        self.gamedisplay.set_face_happy()

    @own_game_mode
    @notended
    @checkbounds
    @notopened
    @notflagged
    def tile_open(self, hn, e):
        width, height = self.gamedisplay.board_size
        row, col = e.row, e.col

        # FIRST CLICK SETUP
        if self.state == "notstarted":
            self.start_game(row, col)

        self.vid.add_command(["OPEN", e.time, row, col])
        self._add_seed(["OPEN", e.time//1000, row, col])

        # Determine the tiles around it before doing anything else
        self.determine_around_tile(row, col)

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

    def determine_all_tiles(self):
        width, height = self.gamedisplay.board_size

        for row in range(height):
            for col in range(width):
                self.determine_tile(row, col)

    def determine_around_tile(self, row, col):
        for drow in range(-1, 2):
            for dcol in range(-1, 2):
                row_, col_ = row + drow, col + dcol
                self.determine_tile(row_, col_)

    def determine_tile(self, row, col):
        width, height = self.gamedisplay.board_size
        if (not (0 <= row < height and 0 <= col < width) or
                (row, col) in self.determined):
            return

        numspaces = len(self.notdetermined)
        nummines = self.num_mines - len(self.mines)
        ismine = self.rng.random(nummines, numspaces)

        self.determined.append((row, col))
        self.notdetermined.remove((row, col))
        if ismine:
            self.mines.append((row, col))
        curtime = pysweep.time()
        self.vid.add_command(["GENERATE", curtime, row, col, ismine])
        self._add_seed(["GENERATE", curtime//1000, row, col, ismine])

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

    @own_game_mode
    @notended
    @notopened
    def tile_toggle_flag(self, hn, e):
        width, height = self.gamedisplay.board_size
        row, col = e.row, e.col

        if (row, col) in self.flagged:

            self.vid.add_command(["UNFLAG", e.time, row, col])
            self._add_seed(["UNFLAG", e.time//1000, row, col])
            self.flagged.remove((row, col))
            self.gamedisplay.set_tile_unopened(row, col)
        else:

            self.vid.add_command(["FLAG", e.time, row, col])
            self._add_seed(["FLAG", e.time//1000, row, col])
            self.flagged.append((row, col))
            self.gamedisplay.set_tile_flag(row, col)

        self.gamedisplay.set_mine_counter(self.num_mines - len(self.flagged))

    @own_game_mode
    @notended
    @opened
    def tile_chord(self, hn, e):
        width, height = self.gamedisplay.board_size
        row, col = e.row, e.col

        self.vid.add_command(["CHORD", e.time, row, col])
        self._add_seed(["CHORD", e.time//1000, row, col])

        squarenum = self.gamedisplay.get_tile_number(row, col)
        flagcount = self.num_flags_around(row, col)
        if flagcount == squarenum:
            # Square is fulfilled. Time to chord!
            for drow in range(-1, 2):
                for dcol in range(-1, 2):
                    e.row, e.col = row+drow, col+dcol
                    self.tile_open(hn, e) # tile_open knows not to open flags


mods = {"PySweeper": PySweeper}
