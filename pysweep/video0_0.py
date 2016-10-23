"""
Parses and outputs videos in the 0.0 format.

As it is right now, this class will seem extremely useless. It puts in what
you tell it to! The idea is that after we release, if we ever push a new version,
we can get this file to read in 0.0 format but give us updated events, etc., while
the new class reads in a new format and gives us the same events (or more).
"""

import time
import ast
import zlib

video_file_version = "PySweeper Video File Format v0.0 (mega unstable)"
pysweeper_version = "PySweeper v0.0 (mega unstable)"

def _video_version():
    return ["VIDEOVERSION", video_file_version]
def _version():
    return ["VERSION", pysweeper_version]
def _time():
    return ["TIME", time.time()]
def _seconds():
    return ["SECONDS", int(time.time())]

def _gamedisplay_positions(gamedisplay):
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
        lambda root,name,widget:
            [
                name,
                widget.winfo_rootx() - root.winfo_rootx(),
                widget.winfo_rooty() - root.winfo_rooty(),
                widget.winfo_width(),
                widget.winfo_height(),
            ],
        *zip(*widgets))

def _board_info(gamedisplay):
    return [
        ["TILESIZE",  gamedisplay.tile_size ],
        ["BOARDSIZE", gamedisplay.board_size],
    ]

def _game_info(gamemode, gameoptions, num_mines):
    return [
        ["GAMEMODE",    gamemode   ],
        ["GAMEOPTIONS", gameoptions],
        ["NUMMINES",  num_mines    ],
    ]

def _add_seed(seed):
    return ["ADDSEED", seed]

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
        return []

class VideoFile0_0_0_0: # video file format 0.0, compatible with PySweeper 0.0
    video_file_version = video_file_version

    vid = []

    @property
    def vidstr(self):
        return str(self.vid)

    def __init__(self, gamedisplay, gamemode, gameoptions, num_mines):
        # Put some stuff in quickly
        self.vid = []
        self.vid.append(_video_version())
        self.vid.append(_version())
        self.vid.append(_time())
        self.vid.append(_seconds())
        self.vid.extend(_gamedisplay_positions(gamedisplay))
        self.vid.extend(_board_info(gamedisplay))
        self.vid.extend(_game_info(gamemode, gameoptions, num_mines))

    def add_seed(self, seed):
        self.vid.append(_add_seed(seed))

    def clicker_event(self, e):
        # Call this on "M", "LD", "LU", "RD", "RU".
        # Don't worry about the hook name, clicker events contain them! :D
        self.vid.extend(_clicker_event(e))
