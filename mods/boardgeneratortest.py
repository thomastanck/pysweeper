import tkinter

from pysweep.util import gamemode
from pysweep import HashRandom

import time
import random

game_mode_name = "Board Generator Test"
class BoardGeneratorTest:
    hooks = {}
    required_events = [
        ("pysweep", "<F2>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("gamedisplaymanager", "FaceDepress"):   [self.face_depress],
            ("gamedisplaymanager", "FaceUndepress"): [self.face_undepress],
            ("gamedisplaymanager", "FaceClicked"): [self.generate_mines],

            ("pysweep", "<F2>"): [self.generate_mines],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

        self.gamedisplay = self.pysweep.gamedisplay

    @gamemode(game_mode_name)
    def face_depress(self, hn, e):
        self.gamedisplay.set_face_pressed()
    @gamemode(game_mode_name)
    def face_undepress(self, hn, e):
        self.gamedisplay.set_face_happy()

    @gamemode(game_mode_name)
    def generate_mines(self, hn, e):
        width, height = self.gamedisplay.board_size
        area = width*height
        self.minecount = 0

        self.rng = HashRandom()
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
                    self.gamedisplay.set_tile_mine(row, col)
                else:
                    self.gamedisplay.set_tile_unopened(row, col)
        self.gamedisplay.set_mine_counter(self.minecount)

mods = {"BoardGeneratorTest": BoardGeneratorTest}
