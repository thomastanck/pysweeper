"""
Parses and outputs videos in the 0.0 format.

As it is right now, this class will seem extremely useless. It puts in what
you tell it to! The idea is that after we release, if we ever push a new version,
we can get this file to read in 0.0 format but give us updated events, etc., while
the new class reads in a new format and gives us the same events (or more).
"""

import pysweep

import json
import zlib

from pysweep import GameDisplayEvent

class VideoFileFactory:
    hooks = {}
    required_events = []
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

            ("gamedisplay", "TileNumber"): [self.display_event],
            ("gamedisplay", "TileOther") : [self.display_event],
            ("gamedisplay", "Counter")   : [self.display_event],
            ("gamedisplay", "Face")      : [self.display_event],
            ("gamedisplay", "Timer")     : [self.display_event],
        }

        self.video_files = []

    def new_video_file(self, *args):
        vidfile = VideoFile0_0_0_0(*args)
        self.video_files.append(vidfile)
        return vidfile

    def del_video_file(self, vidfile):
        self.video_files.remove(vidfile)

    def clicker_event(self, hn, e):
        for vid in self.video_files:
            vid.clicker_event(e)
    def display_event(self, hn, e):
        for vid in self.video_files:
            vid.display_event(e)

video_file_version = "PySweeper Video File Format v0.0 (mega unstable)"
pysweeper_version = "PySweeper v0.0 (mega unstable)"

def _video_version():
    return ["VIDEOVERSION", video_file_version]
def _version():
    return ["VERSION", pysweeper_version]
def _time():
    return ["TIME", pysweep.time()]
def _seconds():
    return ["SECONDS", pysweep.seconds()]

def _gamedisplay_positions(gamedisplay):
    gamedisplay.display.update_idletasks()
    widgets = [
        (gamedisplay.display, "DISPLAY"            , gamedisplay.display                    ),
        (gamedisplay.display, "PANEL"              , gamedisplay.panel                      ),
        (gamedisplay.display, "MINECOUNTER"        , gamedisplay.mine_counter               ),
        (gamedisplay.display, "FACEBUTTON"         , gamedisplay.face_button                ),
        (gamedisplay.display, "TIMER"              , gamedisplay.timer                      ),
        (gamedisplay.display, "BOARD"              , gamedisplay.board                      ),
        (gamedisplay.display, "BORDER_TOP_LEFT"    , gamedisplay.display.border_top_left    ),
        (gamedisplay.display, "BORDER_TOP"         , gamedisplay.display.border_top         ),
        (gamedisplay.display, "BORDER_TOP_RIGHT"   , gamedisplay.display.border_top_right   ),
        (gamedisplay.display, "BORDER_PANEL_LEFT"  , gamedisplay.display.border_panel_left  ),
        (gamedisplay.display, "BORDER_PANEL_RIGHT" , gamedisplay.display.border_panel_right ),
        (gamedisplay.display, "BORDER_MID_LEFT"    , gamedisplay.display.border_mid_left    ),
        (gamedisplay.display, "BORDER_MID"         , gamedisplay.display.border_mid         ),
        (gamedisplay.display, "BORDER_MID_RIGHT"   , gamedisplay.display.border_mid_right   ),
        (gamedisplay.display, "BORDER_LEFT"        , gamedisplay.display.border_left        ),
        (gamedisplay.display, "BORDER_RIGHT"       , gamedisplay.display.border_right       ),
        (gamedisplay.display, "BORDER_BOT_LEFT"    , gamedisplay.display.border_bot_left    ),
        (gamedisplay.display, "BORDER_BOT"         , gamedisplay.display.border_bot         ),
        (gamedisplay.display, "BORDER_BOT_RIGHT"   , gamedisplay.display.border_bot_right   ),
    ]
    return map(
        lambda tup:
            [
                tup[1],
                tup[2].winfo_rootx() - tup[0].winfo_rootx(),
                tup[2].winfo_rooty() - tup[0].winfo_rooty(),
                tup[2].winfo_width(),
                tup[2].winfo_height(),
            ],
        widgets)

def _board_info(gamedisplay):
    return [
        ["TILESIZE",  gamedisplay.tile_size[0] , gamedisplay.tile_size[1] ],
        ["BOARDSIZE", gamedisplay.board_size[0], gamedisplay.board_size[1]],
    ]

def _game_info(gamemode, gameoptions):
    return [
        ["GAMEMODE",    gamemode   ],
        ["GAMEOPTIONS", gameoptions],
    ]

def _clicker_event(e):
    command_map = {
        "M" : "MOVE",
        "LD": "LMBDOWN",
        "RD": "RMBDOWN",
        "LU": "LMBUP",
        "RU": "RMBUP",
    }
    if e.event in command_map:
        return [[command_map[e.event], e.time, e.x, e.y]]
    else:
        raise TypeError('Illegal Event. Should only pass in ClickerEvent\'s which are M, LD, RD, LU, RU only.')

def _display_event(e):
    # Just do some validation and put the event in
    command_map = {
        "TileNumber": "TILENUMBER",
        "TileOther" : "TILEOTHER" ,
        "Counter"   : "COUNTER"   ,
        "Face"      : "FACE"      ,
        "Timer"     : "TIMER"     ,
    }
    if e.event in command_map:
        if e.event == "TileNumber" or e.event == "TileOther":
            return [[command_map[e.event], e.time, e.arg, e.row, e.col]]
        else:
            return [[command_map[e.event], e.time, e.arg]]
    else:
        raise TypeError('Illegal Event. Should only pass in DisplayEvent\'s which are DEPRESS, UNDEPRESS, TILENUMBER, TILEOTHER, COUNTER, FACE, TIMER only.')

class VideoFile0_0_0_0: # video file format 0.0, compatible with PySweeper 0.0
    video_file_version = video_file_version

    vid = []

    def __init__(self, gamedisplay, gamemode, gameoptions):
        # Put some stuff in quickly
        self.vid = []
        self.vid.append(_video_version())
        self.vid.append(_version())
        self.vid.append(_time())
        self.vid.append(_seconds())
        self.vid.extend(_gamedisplay_positions(gamedisplay))
        self.vid.extend(_board_info(gamedisplay))
        self.vid.extend(_game_info(gamemode, gameoptions))

        self.recording = False
        self.after_display_change = False

    def start(self):
        self.recording = True
        self.after_display_change = True
    def start_after_display_change(self):
        self.recording = True
        self.after_display_change = False
    def stop(self):
        self.recording = False
        self.after_display_change = False

    @property
    def vidstr(self):
        return json.dumps(self.vid)
    @vidstr.setter
    def vidstr(self, vidstr):
        self.vid = json.loads(vidstr)

    @property
    def vidbytes(self):
        return zlib.compress(self.vidstr.encode('utf-8'), 9)
    @vidbytes.setter
    def vidbytes(self, vidbytes):
        self.vidstr = zlib.decompress(vidbytes).decode('utf-8')

    def clicker_event(self, e):
        # Call this on "M", "LD", "LU", "RD", "RU".
        # Don't worry about the hook name, clicker events contain them! :D
        if self.recording:
            if self.after_display_change:
                self.vid.extend(_clicker_event(e))

    def display_event(self, e):
        if self.recording:
            self.after_display_change = True
            self.vid.extend(_display_event(e))

    def add_command(self, command):
        if type(command) != list or type(command[0]) != str:
            raise TypeError('Commands must be lists where the first element is a string')
        self.vid.append(command)


mods = {"VideoFile0_0_0_0": VideoFileFactory, "VideoFile": VideoFileFactory}
