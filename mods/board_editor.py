import tkinter

from pysweep.util import own_game_mode
from pysweep.mods import Face
import pysweep

class BoardEditor(Face):
    hooks = {}
    required_events = []
    game_mode_name = "Board Editor"

    def __init__(self, master, pysweep):
        super().__init__(master, pysweep)
        self.hooks.update({
            ("pysweep", "AllModsLoaded"): [self.modsloaded],
            ("gamemode", "EnableGameMode"): [self.onenable],
            ("gamemode", "DisableGameMode"): [self.ondisable],
            ("gamedisplaymanager", "TileLU"): [self.toggle_square],
            ("gamedisplaymanager", "TileLD"): [self.tile_down],
        })
        self._stats_box_geometry = None

        self.board = BoardState(self.gamedisplay.board.board_width,
                                self.gamedisplay.board.board_height)

    
    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods['GameModeSelector']
        self.gamemodeselector.register_game_mode(self.game_mode_name)

        self.menu = tkinter.Menu(pysweep.Menu.menubar, tearoff=0)
        self.menu.add_command(label="Save", command=self.save_board)
        self.menu.add_command(label="Load", command=self.load_board)
        self.menu.add_separator()

        self.menu_toggles = {
            'stats_box': tkinter.IntVar(value=1),
            'show_numbers': tkinter.IntVar(),
            'use_flags': tkinter.IntVar()
        }

        self.menu.add_checkbutton(label="Toggle stats box",
                                  variable=self.menu_toggles['stats_box'],
                                  command=self.show_hide_stats_box)
        self.menu.add_checkbutton(label="Show numbers",
                                  variable=self.menu_toggles['show_numbers'],
                                  command=self.update)
        self.menu.add_checkbutton(label="Use flags",
                                  variable=self.menu_toggles['use_flags'],
                                  command=self.update)
        self.menu.add_separator()
        self.menu.add_command(label="Set size", command=self.set_size_dialog)

    def create_stats_box(self):
        self.stats_box = StatsBox(self, "Board stats")

    @own_game_mode
    def onenable(self, hn, e):
        pysweep.Menu.add_menu("Options", self.menu)
        self.create_stats_box()
        if self._stats_box_geometry is not None:
            self.stats_box.geometry(self._stats_box_geometry)
        self.update()

    @own_game_mode
    def ondisable(self, hn, e):
        pysweep.Menu.remove_menu("Options", self.menu)
        self._stats_box_geometry = self.stats_box.geometry()
        self.stats_box.destroy()

    @own_game_mode
    def toggle_square(self, hn, e):
        row, col = e.row, e.col

        self.board.toggle_square(row, col)
        self.update()

        self.gamedisplay.set_face_happy()

    @own_game_mode
    def tile_down(self, hn, e):
        self.gamedisplay.set_face_nervous()

    def face_button(self, hn, e):
        self.board.reset()
        self.update()

    def load_board(self):
        print("load_board")

    def save_board(self):
        print("save_board")

    def show_hide_stats_box(self, *args, **kwargs):
        if self.menu_toggles['stats_box'].get():
            self.stats_box.show()
        else:
            self.stats_box.hide()

    def toggle_stats_box(self):
        val = self.menu_toggles['stats_box'].get()
        self.menu_toggles['stats_box'].set(0 if val else 1)
        self.show_hide_stats_box()

    def set_size(self):
        self.gamedisplay.set_size(width, height)
        self.board = BoardState(width, height)
        self.update()

    def set_size_dialog(self):
        SetSizeDialog(self, self.set_size)

    def update(self):
        use_flags = self.menu_toggles['use_flags'].get()
        show_numbers = self.menu_toggles['show_numbers'].get()
        for row, col, mine in self.board:
            if mine:
                if use_flags:
                    self.gamedisplay.set_tile_flag(row, col)
                else:
                    self.gamedisplay.set_tile_mine(row, col)
            else:
                if show_numbers:
                    number = self.board.num_neighbours(row, col)
                    self.gamedisplay.set_tile_number(row, col, number)
                else:
                    self.gamedisplay.set_tile_unopened(row, col)
        mines = self.board.mines
        self.gamedisplay.set_mine_counter(mines)
        self.stats_box.set_value('mines', mines)

class StatsEntry:
    def __init__(self, label, variable_name, value=''):
        self.label = label
        self.variable_name = variable_name
        self.value = tkinter.StringVar(value=str(value))

    def create_label(self, parent):
        self.parent = parent
        style = {
            'bd': 0,
            'anchor': "nw"
        }
        self.label_label = tkinter.Label(parent, text=self.label, **style)
        self.value_label = tkinter.Label(parent, textvariable=self.value, **style)

    def grid(self, row):
        self.label_label.grid(row=row, column=0, sticky="EW")
        self.value_label.grid(row=row, column=1, sticky="EW")

    def set_value(self, value):
        self.value.set(value)

class StatsBox(tkinter.Toplevel):
    entries = [
        StatsEntry("Mines", "mines", 0),
        StatsEntry("3bv", "bbbv", 123),
        StatsEntry("Openings", "openings"),
        StatsEntry("Islands", "islands"),
    ]

    style = {
        'bd': 0,
        'relief': 'solid',
        'padx': 10,
        'pady': 4
    }

    def __init__(self, parent, title):
        super().__init__(parent.master)
        self.title(title)
        self.parent = parent
        self.resizable(width=False, height=False)
        self.transient(parent.master)
        self._last_geometry = None
        self.protocol("WM_DELETE_WINDOW", self.parent.toggle_stats_box)

        self.labels = {}
        self.create_labels()
        for column in range(2):
            self.grid_columnconfigure(column, minsize=75)
        self.config(**self.style)

    def hide(self):
        self._last_geometry = self.geometry()
        self.withdraw()

    def show(self):
        if self._last_geometry is not None:
            self.geometry(self._last_geometry)
        self.deiconify()

    def create_labels(self):
        for i, entry in enumerate(self.entries):
            entry.create_label(self)
            entry.grid(row=i)

    def set_value(self, name, value):
        for entry in self.entries:
            if entry.variable_name == name:
                break
        else:
            return
        entry.set_value(value)


class SetSizeDialog(tkinter.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent.master)
        self.callback = callback
        self.parent = parent


class BoardState:
    def __init__(self, width, height):
        self.grid = [[0]*width for __ in range(height)]

    def num_neighbours(self, row, col):
        val = 0
        for r in self.grid[max(row-1, 0):row+2]:
            for c in r[max(col-1, 0):col+2]:
                val += c
        return val

    @property
    def mines(self):
        total = 0
        for r in self.grid:
            for c in r:
                total += c
        return total

    def get(self, row, col):
        return self.grid[row][col]

    def toggle_square(self, row, col):
        value = self.grid[row][col]
        new_val = 0 if value else 1
        self.grid[row][col] = new_val

    def __iter__(self):
        for row_num, row in enumerate(self.grid):
            for col_num, mine in enumerate(row):
                yield row_num, col_num, mine

    def reset(self):
        for row in self.grid:
            for i in range(len(row)):
                row[i] = 0


        
mods = {"BoardEditor": BoardEditor}
