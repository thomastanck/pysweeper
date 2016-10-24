import tkinter

from pysweep.util import gamemode
from pysweep import HashRandom#, VideoFile

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
            ("gamedisplaymanager", "TileOpen"):      [self.tile_open],
            ("gamedisplaymanager", "TileDepress"):   [self.tile_depress],
            ("gamedisplaymanager", "TileUndepress"): [self.tile_undepress],
            ("gamedisplaymanager", "FaceDepress"):   [self.face_depress],
            ("gamedisplaymanager", "FaceUndepress"): [self.face_undepress],

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

    @gamemode(game_mode_name)
    def onenable(self, hn, e):
        self.video_file = self.videofilemod.new_video_file(self.gamedisplay, game_mode_name, "N/A")
        self.video_file.start()
    @gamemode(game_mode_name)
    def ondisable(self, hn, e):
        self.video_file.stop()
        self.videofilemod.del_video_file(self.video_file)
        self.video_file = None

    @gamemode(game_mode_name)
    def tile_open(self, hn, e):
        self.gamedisplay.set_tile_number(e.row, e.col, 0)

    @gamemode(game_mode_name)
    def tile_depress(self, hn, e):
        self.gamedisplay.set_tile_number(e.row, e.col, 0)
        self.gamedisplay.set_face_nervous()
    @gamemode(game_mode_name)
    def tile_undepress(self, hn, e):
        self.gamedisplay.set_tile_unopened(e.row, e.col)
        self.gamedisplay.set_face_happy()
    @gamemode(game_mode_name)
    def face_depress(self, hn, e):
        self.gamedisplay.set_face_pressed()
    @gamemode(game_mode_name)
    def face_undepress(self, hn, e):
        self.gamedisplay.set_face_happy()


    @gamemode(game_mode_name)
    def print_vidfile(self, hn, e):
        print(self.video_file.vidstr)
        print("vidstr len: {}, vidbytes len: {}".format(len(self.video_file.vidstr), len(self.video_file.vidbytes)))

mods = {"VideoFileTest": VideoFileTest}
