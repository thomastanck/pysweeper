import tkinter

class GameModeSelector:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.window = tkinter.Toplevel(self.master)
        self.window.title("Game Mode")
        # self.window
        self.gamemodes = []
        self.currentgamemode = None

    def register_game_mode(self, gamemodename):
        self.gamemodes.append(gamemodename)
        button = tkinter.Button(self.window, text=gamemodename, command=lambda gamemodename=gamemodename: self.set_game_mode(gamemodename))

        button.pack()

    def set_game_mode(self, gamemodename):
        self.currentgamemode = gamemodename

    def is_enabled(self, gamemodename):
        return self.currentgamemode == gamemodename
