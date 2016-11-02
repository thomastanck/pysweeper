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

    
    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods['GameModeSelector']
        self.gamemodeselector.register_game_mode(self.game_mode_name)

        self.menu = tkinter.Menu(pysweep.Menu.menubar, tearoff=0)
        self.menu.add_command(label="Save", command=self.save_board)
        self.menu.add_command(label="Load", command=self.load_board)
        self.menu.add_separator()

        #stats_box.set(1) # We default to showing the stats box
        self.menu_toggles = {
            'stats_box': tkinter.IntVar(value=1),
            'show_numbers': tkinter.IntVar()
        }

        self.menu.add_checkbutton(label="Toggle stats box",
                                  variable=self.menu_toggles['stats_box'],
                                  command=self.toggle_stats)
        self.menu.add_checkbutton(label="Show numbers",
                                  variable=self.menu_toggles['show_numbers'])

    def create_stats_box(self):
        self.stats_box = StatsBox(self.master, "Board stats")

    @own_game_mode
    def onenable(self, hn, e):
        pysweep.Menu.add_menu("Options", self.menu)
        self.create_stats_box()

    @own_game_mode
    def ondisable(self, hn, e):
        pysweep.Menu.remove_menu("Options", self.menu)
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

    def toggle_stats(self, *args, **kwargs):
        if self.menu_toggles['stats_box'].get():
            self.stats_box.show()
        else:
            self.stats_box.hide()

class StatsBox(tkinter.Toplevel):
    def __init__(self, master, title):
        super().__init__(master)
        self.title = title
        self.resizable(width=False, height=False)
        self.transient(master)
        self._last_geometry = None

    def hide(self):
        self._last_geometry = self.geometry()
        self.withdraw()

    def show(self):
        if self._last_geometry is not None:
            self.geometry(self._last_geometry)
        self.deiconify()
        
mods = {"BoardEditor": BoardEditor}
