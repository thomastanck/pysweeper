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
        self.window = tkinter.Toplevel(self.master)
        self.rewindbutton = tkinter.Button(self.window, text="Bek", command=self.rewind)
        self.playbutton = tkinter.Button(self.window, text="Purei", command=self.play)
        self.forwardbutton = tkinter.Button(self.window, text="Foowaado", command=self.forward)
        # step forward backward, other images and stuff, etc
        # You'll probably want Frames and Canvases in here.
        self.rewindbutton.pack()
        self.playbutton.pack()
        self.forwardbutton.pack()

    @gamemode(game_mode_name)
    def on_disable(self, hn, e):
        print("disabled!")
        self.window.destroy()
        self.window = null

    def rewind(self):
        print("rewind pressed")
    def play(self):
        print("play pressed")
    def forward(self):
        print("forward pressed")


mods = {"Player": Player}