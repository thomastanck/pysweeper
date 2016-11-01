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

        self.menuvar = tkinter.StringVar()
        self.menu = tkinter.Menu(pysweep.Menu.menubar, tearoff=0)
        self.menu.add_radiobutton(label="Save", variable=self.menuvar)
        self.menu.add_radiobutton(label="Load", variable=self.menuvar)
        self.menu.add_radiobutton(label="Toggle stats box", variable=self.menuvar)
        self.menu.add_radiobutton(label="Show numbers", variable=self.menuvar)

    @own_game_mode
    def onenable(self, hn, e):
        pysweep.Menu.add_menu("Options", self.menu)

    @own_game_mode
    def ondisable(self, hn, e):
        pysweep.Menu.remove_menu("Options", self.menu)

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

        
mods = {"BoardEditor": BoardEditor}
