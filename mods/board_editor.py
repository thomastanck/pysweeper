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
        self.mine_count = 0
        self._stats_box_geometry = None

    
    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods['GameModeSelector']
        self.gamemodeselector.register_game_mode(self.game_mode_name)

        self.menu = tkinter.Menu(pysweep.Menu.menubar, tearoff=0)
        self.menu.add_command(label="Save", command=self.save_board)
        self.menu.add_command(label="Load", command=self.load_board)
        self.menu.add_separator()

        self.menu_toggles = {
            'stats_box': tkinter.IntVar(value=1),
            'show_numbers': tkinter.IntVar()
        }

        self.menu.add_checkbutton(label="Toggle stats box",
                                  variable=self.menu_toggles['stats_box'],
                                  command=self.show_hide_stats_box)
        self.menu.add_checkbutton(label="Show numbers",
                                  variable=self.menu_toggles['show_numbers'])

    def create_stats_box(self):
        self.stats_box = StatsBox(self, "Board stats")

    @own_game_mode
    def onenable(self, hn, e):
        pysweep.Menu.add_menu("Options", self.menu)
        self.create_stats_box()
        if self._stats_box_geometry is not None:
            self.stats_box.geometry(self._stats_box_geometry)

    @own_game_mode
    def ondisable(self, hn, e):
        pysweep.Menu.remove_menu("Options", self.menu)
        self._stats_box_geometry = self.stats_box.geometry()
        self.stats_box.destroy()

    @own_game_mode
    def toggle_square(self, hn, e):
        row, col = e.row, e.col
        if self.gamedisplay.is_tile_mine(row, col):
            self.gamedisplay.set_tile_unopened(row, col)
            self.mine_count -= 1
        elif self.gamedisplay.is_tile_unopened(row, col):
            self.gamedisplay.set_tile_mine(row, col)
            self.mine_count += 1

        self.gamedisplay.set_face_happy()
        self.gamedisplay.set_mine_counter(self.mine_count)

    @own_game_mode
    def tile_down(self, hn, e):
        self.gamedisplay.set_face_nervous()

    def face_button(self, hn, e):
        self.gamedisplay.reset_board()
        self.mine_count = 0
        self.gamedisplay.set_mine_counter(self.mine_count)

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

class StatsEntry:
    def __init__(self, label, variable_name, value=''):
        self.label = label
        self.variable_name = variable_name
        self.value = tkinter.StringVar(value=str(value))

    def create_label(self, parent):
        self.parent = parent
        style = {
            'bd': 1,
            'relief': 'solid'
        }
        self.label_label = tkinter.Label(parent, text=self.label, **style)
        self.value_label = tkinter.Label(parent, textvariable=self.value, **style)

    def grid(self, row):
        self.label_label.grid(row=row, column=0, sticky="EW")
        self.value_label.grid(row=row, column=1, sticky="EW")

class StatsBox(tkinter.Toplevel):
    entries = [
        StatsEntry("3bv", "bbbv", 123),
        StatsEntry("Openings", "openings"),
        StatsEntry("Islands", "islands"),
    ]

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

        
mods = {"BoardEditor": BoardEditor}
