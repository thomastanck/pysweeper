import tkinter

import time
import random

game_mode_name = "Board Generator Test"
class BoardGeneratorTest:
    game_mode_name = game_mode_name
    hooks = {}
    required_events = [
        ("face_button", "<ButtonPress-1>"),
        ("face_button", "<ButtonRelease-1>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            ("face_button", "<ButtonPress-1>"):   [self.press_smiley],
            ("face_button", "<ButtonRelease-1>"): [self.generate_mines],

            ("pysweep3", "<F2>"): [self.generate_mines],

            ("pysweep3", "AllModsLoaded"): [self.modsloaded],

            ("gamemode", "EnableGameMode"): [self.log],
            ("gamemode", "DisableGameMode"): [self.log],
        }

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep3.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

        self.gamedisplay = self.pysweep3.mods["GameDisplay"]
        width, height = self.gamedisplay.display.board_width, self.gamedisplay.display.board_height

        self.rngmod = self.pysweep3.mods["HashRandom"]

    def press_smiley(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.display.panel.face_button.set_face("pressed")

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
                self.rng.update("GEN {} {}\n".format(row, col))
                ismine = self.rng.random(mines_left, squares_left)
                squares_left -= 1
                if ismine:
                    self.minecount += 1
                    mines_left -= 1
                    self.set_tile(row, col, "mine")
                else:
                    self.set_tile(row, col, "unopened")
        # print(self.rng.get_source())
        self.gamedisplay.display.panel.mine_counter.set_value(self.minecount)
        self.gamedisplay.display.panel.face_button.set_face("happy")

    def log(self, hn, e):
        print(hn, e, type(e))

    def get_tile_type(self, i, j):
        board = self.gamedisplay.display.board
        return board.get_tile_type(i, j)

    def set_tile(self, i, j, tile_type):
        board = self.gamedisplay.display.board
        board.set_tile(i, j, tile_type)

mods = {"BoardGeneratorTest": BoardGeneratorTest}
