import tkinter

import time
import random

game_mode_name = "Board Generator Test"
class BoardGeneratorTest:
    hooks = {}
    required_events = [
        ("pysweep", "<ButtonPress-1>"),
        ("pysweep", "<B1-Motion>"),
        ("pysweep", "<ButtonRelease-1>"),
        ("face_button", "<ButtonPress-1>"),
        ("face_button", "<ButtonRelease-1>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<ButtonPress-1>"):   [self.handle_mouse_event],
            ("pysweep", "<B1-Motion>"):       [self.handle_mouse_event],
            ("pysweep", "<ButtonRelease-1>"): [self.handle_mouse_event],

            ("gamedisplaymanager", "FaceClicked"): [self.generate_mines],

            ("pysweep", "<F2>"): [self.generate_mines],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

        self.gamedisplay = self.pysweep.mods["GameDisplay"]

        self.gamedisplaymanager = self.pysweep.mods["GameDisplayManager"]

        self.rngmod = self.pysweep.mods["HashRandom"]

    def handle_mouse_event(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplaymanager.handle_mouse_event(hn, e)

    def generate_mines(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        width, height = self.gamedisplay.size
        area = width*height
        self.minecount = 0

        self.rng = self.rngmod.get_rng()
        self.rng.update("TIME {}\n".format(time.time()))
        self.rng.update("RANDOM {}\n".format(random.random()))

        mines_left = 99
        squares_left = area
        for row in range(height):
            for col in range(width):
                # NB: No need to put in self-generated entropy per square we calculate.
                # There is no actual new entropy here between each cycle. This is handled
                # in the HashRandom class
                # self.rng.update("GEN {} {}\n".format(row, col))
                ismine = self.rng.random(mines_left, squares_left)
                squares_left -= 1
                if ismine:
                    self.minecount += 1
                    mines_left -= 1
                    self.gamedisplaymanager.set_tile_mine(row, col)
                else:
                    self.gamedisplaymanager.set_tile_unopened(row, col)
        self.gamedisplaymanager.update()
        self.gamedisplay.display.panel.mine_counter.set_value(self.minecount)
        self.gamedisplay.display.panel.face_button.set_face("happy")

mods = {"BoardGeneratorTest": BoardGeneratorTest}
