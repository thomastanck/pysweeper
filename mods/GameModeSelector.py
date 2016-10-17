import tkinter

class GameModeSelector:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            "AllModsLoaded": [self.modsloaded],
        }

        self.gamemodes = []
        self.currentgamemode = None
        self.menumod = None

    def modsloaded(self, e):
        if not self.menumod:
            self.menumod = self.pysweep3.mods["Menu"]
            self.menu = tkinter.Menu(self.menumod.menubar, tearoff=0)
            self.menu.add_separator()
            self.menu.add_radiobutton(label="None", command=self.cancel)
            self.menu.invoke(1)
            self.menumod.add_menu("Game", self.menu)

    def cancel(self):
        self.currentgamemode = None

    def register_game_mode(self, gamemodename):
        if not self.menumod:
            self.modsloaded(None)

        self.menu.insert_radiobutton(len(self.gamemodes), label=gamemodename, command=lambda gamemodename=gamemodename: self.set_game_mode(gamemodename))
        self.gamemodes.append(gamemodename)

    def set_game_mode(self, gamemodename):
        self.currentgamemode = gamemodename

    def is_enabled(self, gamemodename):
        return self.currentgamemode == gamemodename
