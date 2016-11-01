import tkinter

from pysweep.util import gamemode, own_game_mode
import pysweep

class BoardEditor:
    hooks = {}
    required_events = []
    game_mode_name = "Board Editor"

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "AllModsLoaded"): [self.modsloaded],
            ("gamemode", "EnableGameMode"): [self.onenable],
            ("gamemode", "DisableGameMode"): [self.ondisable],
        }
    
    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods['GameModeSelector']
        self.gamemodeselector.register_game_mode(self.game_mode_name)

        self.menuvar = tkinter.StringVar()
        self.menu = tkinter.Menu(pysweep.Menu.menubar, tearoff=0)
        self.menu.add_radiobutton(label="Edit", variable=self.menuvar)

    @own_game_mode
    def onenable(self, hn, e):
        pysweep.Menu.add_menu("Options", self.menu)

    @own_game_mode
    def ondisable(self, hn, e):
        pysweep.Menu.remove_menu("Options", self.menu)
        
mods = {"BoardEditor": BoardEditor}
