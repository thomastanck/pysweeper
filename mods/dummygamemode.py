import tkinter

import random

class DummyGameMode:
    hooks = {}
    required_events = [
        ("pysweep", "<ButtonPress-1>"),
        ("pysweep", "<B1-Motion>"),
        ("pysweep", "<ButtonRelease-1>"),

        ("pysweep", "<KeyPress>"),
        ("pysweep", "<KeyRelease>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<ButtonPress-1>"):   [self.handle_mouse_event],
            ("pysweep", "<B1-Motion>"):       [self.handle_mouse_event],
            ("pysweep", "<ButtonRelease-1>"): [self.handle_mouse_event],

            ("gamedisplaymanager", "TileClicked"): [self.onrelease],

            ("gamedisplaymanager", "FaceClicked"): [self.onrelease_smiley],

            ("pysweep", "<KeyPress>"):   [self.onpress_timer],
            ("pysweep", "<KeyRelease>"): [self.onrelease_timer],

            ("gamedisplaymanager", "MineCounterClicked"): [self.randomiseminecounter],
            ("gamedisplaymanager", "TimerClicked"): [self.randomisetimer],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode("Dummy Game Mode")

        self.gamedisplay = self.pysweep.mods["GameDisplay"]

        self.gamedisplaymanager = self.pysweep.mods["GameDisplayManager"]

        self.timermod = self.pysweep.mods["Timer"]
        self.timer = self.timermod.get_timer(self.timercallback, resolution=0.001)

    def handle_mouse_event(self, hn, e):
        if not self.gamemodeselector.is_enabled("Dummy Game Mode"):
            return
        self.gamedisplaymanager.handle_mouse_event(hn, e)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.display.set_timer(int(elapsed*1000))

    def onpress_timer(self, hn, e):
        if not self.gamemodeselector.is_enabled("Dummy Game Mode"):
            return
        self.timer.start_timer()

    def onrelease_timer(self, hn, e):
        if not self.gamemodeselector.is_enabled("Dummy Game Mode"):
            return
        self.timer.stop_timer()

    def onrelease_smiley(self, hn, e):
        if not self.gamemodeselector.is_enabled("Dummy Game Mode"):
            return
        self.gamedisplay.display.board.reset_board()

    def randomiseminecounter(self, hn, e):
        if not self.gamemodeselector.is_enabled("Dummy Game Mode"):
            return
        self.gamedisplay.display.panel.mine_counter.set_value(random.randint(0,100000000))

    def randomisetimer(self, hn, e):
        if not self.gamemodeselector.is_enabled("Dummy Game Mode"):
            return
        self.gamedisplay.display.set_timer(random.randint(0,100000000))

    def onrelease(self, hn, e):
        row, col = e.y//16, e.x//16
        self.gamedisplaymanager.set_tile_number(row, col, 0)

mods = {"DummyGameMode": DummyGameMode}
