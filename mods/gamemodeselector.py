import tkinter

class GameModeSelector:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

        self.gamemodes = []
        self.currentgamemode = None
        self.menumod = None

    def modsloaded(self, hn, e):
        if not self.menumod:
            self.menumod = self.pysweep.mods["Menu"]
            self.menu = tkinter.Menu(self.menumod.menubar, tearoff=0)
            self.menu.add_separator()
            self.menu.add_radiobutton(label="None", command=self.cancel)
            self.menu.invoke(1)
            self.menumod.add_menu("Game", self.menu)

    def cancel(self):
        if (self.currentgamemode != None):
            self.pysweep.handle_event(("gamemode", "DisableGameMode"), self.currentgamemode)
        self.currentgamemode = None

    def register_game_mode(self, gamemodename):
        if not self.menumod:
            self.modsloaded(("pysweep", "AllModsLoaded"), None)

        self.menu.insert_radiobutton(len(self.gamemodes), label=gamemodename, command=lambda gamemodename=gamemodename: self.set_game_mode(gamemodename))
        self.gamemodes.append(gamemodename)

    def set_game_mode(self, gamemodename):
        if (self.currentgamemode != gamemodename):
            if (self.currentgamemode != None):
                self.pysweep.handle_event(("gamemode", "DisableGameMode"), self.currentgamemode)
            self.currentgamemode = gamemodename
            self.pysweep.handle_event(("gamemode", "EnableGameMode"), gamemodename)

    def is_enabled(self, gamemodename):
        return self.currentgamemode == gamemodename

mods = {"GameModeSelector": GameModeSelector}
