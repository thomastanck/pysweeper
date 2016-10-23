import tkinter

from pysweep.util import gamemode

game_mode_name = "Video Player"

class Player:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "AllModsLoaded"): [self.mods_loaded],
            ("gamemode", "EnableGameMode"): [self.on_enable],
            ("gamemode", "DisableGameMode"): [self.on_disable],
        }

    def mods_loaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

    @gamemode(game_mode_name)
    def on_enable(self, hn, e):
        print("enabled!")

    @gamemode(game_mode_name)
    def on_disable(self, hn, e):
        print("disabled!")


mods = {"Player": Player}
