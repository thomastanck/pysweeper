import tkinter

from pysweep import HashRandom#, VideoFile

import time
import random

game_mode_name = "Video File Test"
class VideoFileTest:
    hooks = {}
    required_events = [
        ("pysweep", "<F2>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("clicker", "M"):  [self.clicker_event],
            ("clicker", "LD"): [self.clicker_event],
            ("clicker", "LU"): [self.clicker_event],
            ("clicker", "RD"): [self.clicker_event],
            ("clicker", "RU"): [self.clicker_event],

            ("pysweep", "<F2>"): [self.print_vidfile],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],

            ("gamemode", "EnableGameMode"):  [self.onenable],
            ("gamemode", "DisableGameMode"): [self.ondisable],
        }

        self.gamedisplay = self.pysweep.gamedisplay

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

        self.videofilemod = self.pysweep.mods["VideoFile"]

    def onenable(self, hn, e):
        if e == game_mode_name:
            self.video_file = self.videofilemod.new_video_file(self.gamedisplay, game_mode_name, "N/A")
    def ondisable(self, hn, e):
        if e == game_mode_name:
            self.videofilemod.del_video_file(self.video_file)
            self.video_file = None

    def clicker_event(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.video_file.clicker_event(e)

    def print_vidfile(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        print(self.video_file.vidstr)
        print("vidstr len: {}, vidbytes len: {}".format(len(self.video_file.vidstr), len(self.video_file.vidbytes)))

mods = {"VideoFileTest": VideoFileTest}
