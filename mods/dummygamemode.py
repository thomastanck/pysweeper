import tkinter

from pysweep import Timer

import random

game_mode_name = "Dummy Game Mode"

class DummyGameMode:
    hooks = {}
    required_events = [
        ("pysweep", "<KeyPress>"),
        ("pysweep", "<KeyRelease>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("gamedisplaymanager", "TileOpen"):      [self.tile_open],
            ("gamedisplaymanager", "TileDepress"):   [self.tile_depress],
            ("gamedisplaymanager", "TileUndepress"): [self.tile_undepress],

            ("gamedisplaymanager", "FaceClicked"): [self.face_clicked],

            ("pysweep", "<KeyPress>"):   [self.onpress_timer],
            ("pysweep", "<KeyRelease>"): [self.onrelease_timer],

            ("gamedisplaymanager", "MineCounterClicked"): [self.randomiseminecounter],
            ("gamedisplaymanager", "TimerClicked"): [self.randomisetimer],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

        self.gamedisplay = self.pysweep.gamedisplay

        self.timer = Timer(self.master, self.timercallback, period=0.001, resolution=0.001)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.set_timer(int(elapsed*1000))

    def onpress_timer(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.timer.start_timer()

    def onrelease_timer(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.timer.stop_timer()

    def face_clicked(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.reset_board()

    def randomiseminecounter(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.set_mine_counter(random.randint(0,100000000))

    def randomisetimer(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.set_timer(random.randint(0,100000000))

    def tile_open(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.set_tile_number(e.row, e.col, 0)

    def tile_depress(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.set_tile_number(e.row, e.col, 0)
        self.gamedisplay.set_face_nervous()
    def tile_undepress(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.set_tile_unopened(e.row, e.col)
        self.gamedisplay.set_face_happy()


mods = {"DummyGameMode": DummyGameMode}
