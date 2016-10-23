"""
# Available hooks:
==================

("gamedisplaymanager", "TileLD") for example.



## Tile events:
----

TileLD: Left down
TileLM: Left move
TileLU: Left up

TileRD: Same but for RMB
TileRM
TileRU

TileD:  Down (any button)
TileM:  Move (any button)
TileU:  Up (any button)

You can TileLD on one tile but never get a TileLU on that tile if you drag
the cursor away! Be careful and listen for TileLM events as well.

(It'll look like TileLD on tile A, followed by TileLM on tile B,
    *more if needed*, and finally TileLU on tile B.)



## More Tile events: (you'll probably want to use these instead)
----

TileDepress:         Depress animation on this tile, single and chord depresses
TileUndepress:       Undepress animation on this tile, single and chord depresses

TileSingleDepress:   ^ but only for LMB
TileSingleUndepress: ^ but only for LMB. Is also called if LMB transitions to a chord

TileChordDepress:    ^^ but only for chording
TileChordUndepress:  ^^ but only for chording

TileOpen:            LMB up without chord
TileChord:           A mouse button up while in chording mode
TileToggleFlag:      RMB down



## Other events:
----

FaceDepress:         Same as TilePress but for the face button
FaceUndepress:       Same as TileRelease but for the face button

FaceClick:           Called on RMB up over the face button
MineCounterClick:    Called on RMB up over the mine counter
TimerClick:          Called on RMB up over the timer
PanelClick:          Called on RMB up over another part of the panel
DisplayClick:        Called on RMB up over another part of the display

"""


# quickie macro to get the proper hook names
def _gh(name): # get hook
    return ("gamedisplaymanager", name)



# For easy referencing, since we check for these events a lot!
LD = ("clicker", "LD")
LM = ("clicker", "LM")
LU = ("clicker", "LU")
RD = ("clicker", "RD")
RM = ("clicker", "RM")
RU = ("clicker", "RU")



class BoardClick:
    # Stripped down version of the tkinter event, and adds some restrictions so it'll be easier to debug in the future
    # One motivation for the attribute restrictions is that we frequently compute row/col out of x/y.
    # In order to prevent mixing up events which are supposed to have x/y and events which are supposed to have row/col,
    # we'll simply force BoardClick to use row/col only.
    __isfrozen = False
    tile_size = (16, 16)
    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError( "%r is a frozen class, cannot set %s" % (self, key))
        object.__setattr__(self, key, value)

    def __init__(self, event=None, time=0, row=0, col=0, lmb=False, rmb=False):
        self.event = event
        self.time = time
        self.row = row
        self.col = col
        self.lmb = lmb
        self.rmb = rmb
        self.__isfrozen = True

    def fromClickerEvent(self, e):
        self.event = e.event # "LD", "LU", "M", etc.
        self.time = e.time
        self.row = e.y//self.tile_size[1]
        self.col = e.x//self.tile_size[0]
        self.lmb = e.lmb
        self.rmb = e.rmb


class GameDisplayManager:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            LD: [self.handle_mouse_event],
            LM: [self.handle_mouse_event],
            LU: [self.handle_mouse_event],
            RD: [self.handle_mouse_event],
            RM: [self.handle_mouse_event],
            RU: [self.handle_mouse_event],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

        self.depressed_tiles = []
        self.current_widget_handler = None
        self.mousedown = False

        self.chording_mode = 0
        # see handle_board for how this works

    def debug(self, hn, e):
        print(hn, e.row, e.col)

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.gamedisplay

    def handle_mouse_event(self, hn, e):
        # We now listen to the events ourselves and output them regardless of game mode.
        widget_handlers = [
            (self.gamedisplay.board,        self.handle_board),
            (self.gamedisplay.face_button,  self.handle_face),
            (self.gamedisplay.mine_counter, self.handle_mine),
            (self.gamedisplay.timer,        self.handle_timer),
            (self.gamedisplay.panel,        self.handle_panel),
            (self.gamedisplay.display,      self.handle_display),
        ]

        for widget, handler in widget_handlers:
            # convert global position to widget position
            x = e.x + e.widget.winfo_rootx() - widget.winfo_rootx()
            y = e.y + e.widget.winfo_rooty() - widget.winfo_rooty()

            # get widget size
            width = widget.winfo_width()
            height = widget.winfo_height()

            if (0 <= x < width and 0 <= y < height):
                # We're in the widget!
                if (self.current_widget_handler and
                        handler != self.current_widget_handler[1] and
                        hn != LD and hn != RD):
                    # convert global position to widget position, this time for the previous widget
                    otherx = e.x + e.widget.winfo_rootx() - self.current_widget_handler[0].winfo_rootx()
                    othery = e.y + e.widget.winfo_rooty() - self.current_widget_handler[0].winfo_rooty()
                    othere = e
                    othere.widget = self.current_widget_handler[0]
                    othere.x, othere.y = otherx, othery
                    othere.inbounds = False
                    self.current_widget_handler[1](hn, othere) # basically emulates Leave events and lets them clean up
                e.widget = widget
                e.x, e.y = x, y
                e.inbounds = True
                handler(hn, e)
                self.current_widget_handler = (widget, handler)
                break # don't allow more than one trigger

    def handle_board(self, hn, e_):
        # Create BoardClick
        BoardClick.tile_size = self.gamedisplay.board.tile_size
        e = BoardClick()
        e.fromClickerEvent(e_)

        # First handle the direct events, TileLU and the like
        if hn == LD:
            self.pysweep.handle_event(_gh("TileLD"), e)
            self.pysweep.handle_event(_gh("TileD"), e)
        elif hn == LM:
            self.pysweep.handle_event(_gh("TileLM"), e)
            self.pysweep.handle_event(_gh("TileM"), e)
        elif hn == LU:
            self.pysweep.handle_event(_gh("TileLU"), e)
            self.pysweep.handle_event(_gh("TileU"), e)
        elif hn == RD:
            self.pysweep.handle_event(_gh("TileRD"), e)
            self.pysweep.handle_event(_gh("TileD"), e)
        elif hn == RM:
            self.pysweep.handle_event(_gh("TileRM"), e)
            self.pysweep.handle_event(_gh("TileM"), e)
        elif hn == RU:
            self.pysweep.handle_event(_gh("TileRU"), e)
            self.pysweep.handle_event(_gh("TileU"), e)

        # As the other board events are more complicated, we split them up.

        # We go into chording mode before handling the event
        # But we leave chording mode only after the event
        if e.lmb > 0 and e.rmb > 0:
            # both buttons down means go into chording mode
            self.board_undepress_tiles(False, e) # Undepress the single-depress tiles before entering chording mode
            self.chording_mode = 1

        if self.chording_mode == 0:
            # Not chording mode, simple rules apply.
            if hn == LD or hn == LM:
                # Depress animation
                self.board_depress(hn, e)
            elif hn == LU:
                # Open square
                self.board_open(hn, e)
            elif hn == RD:
                # Toggle flag
                self.board_toggle_flag(hn, e)
        elif self.chording_mode == 1:
            # Chording mode is simple: depress neighbours until release (which means chord).
            # Further releases will be in after chording mode.
            if hn == LD or hn == LM or hn == RD or hn == RM:
                # Depress animation (chording)
                self.board_depress_chord(hn, e)
            if hn == LU or hn == RU:
                # Chord
                self.board_chord(hn, e)
        else: # self.chording_mode == 2
            # After chording mode
            # We don't do anything here I think...
            pass

        # Leave chording mode
        if (hn == LU or hn == RU) and self.chording_mode == 1:
            # Release while in chording mode goes to after chording mode
            self.chording_mode = 2
        if e.lmb == 0 and e.rmb == 0:
            # both buttons up means reset to normal mode
            self.chording_mode = 0

    def handle_face(self, hn, e):
        if e.inbounds:
            if hn[1] == "LD" or hn[1] == "LM":
                self.gamedisplay.set_face_pressed()
            elif hn[1] == "LU":
                self.pysweep.handle_event(_gh("FaceClicked"), e)
                self.gamedisplay.set_face_happy()
        else:
            self.gamedisplay.set_face_happy()

    # Click only handlers
    def handle_mine(self, hn, e):
        if hn[1] == "LU":
            self.pysweep.handle_event(_gh("MineCounterClicked"), e)
    def handle_timer(self, hn, e):
        if hn[1] == "LU":
            self.pysweep.handle_event(_gh("TimerClicked"), e)
    def handle_panel(self, hn, e):
        if hn[1] == "LU":
            self.pysweep.handle_event(_gh("PanelClicked"), e)
    def handle_display(self, hn, e):
        if hn[1] == "LU":
            self.pysweep.handle_event(_gh("DisplayClicked"), e)


    # Board events
    def board_depress(self, hn, e):
        # Undepress currently depressed cells
        # Depress current cell
        self.board_undepress_tiles(False, e)

        width, height = self.gamedisplay.board_size
        if (0 <= e.col < width and 0 <= e.row < height):
            if self.gamedisplay.get_tile_type(e.row, e.col) == "unopened":
                self.depressed_tiles.append((e.row, e.col))
                self.pysweep.handle_event(_gh("TileDepress"), e)
                self.pysweep.handle_event(_gh("TileSingleDepress"), e)

    def board_open(self, hn, e):
        # Undepress currently depressed cells
        # Send out click event
        self.board_undepress_tiles(False, e)
        width, height = self.gamedisplay.board_size
        if (0 <= e.col < width and 0 <= e.row < height):
            self.pysweep.handle_event(_gh("TileOpen"), e)

    def board_toggle_flag(self, hn, e):
        # Send out click event
        width, height = self.gamedisplay.board_size
        if (0 <= e.col < width and 0 <= e.row < height):
            self.pysweep.handle_event(_gh("TileToggleFlag"), e)

    def board_depress_chord(self, hn, e):
        # Undepress currently depressed cells
        # Depress current cell and neighbours
        self.board_undepress_tiles(True, e)
        width, height = self.gamedisplay.board_size
        for drow in range(-1, 2):
            for dcol in range(-1, 2):
                e_ = BoardClick(e.event, e.time, e.row+drow, e.col+dcol, e.lmb, e.rmb)
                if (0 <= e_.col < width and 0 <= e_.row < height):
                    if self.gamedisplay.get_tile_type(e_.row, e_.col) == "unopened":
                        self.depressed_tiles.append((e_.row, e_.col))
                        self.pysweep.handle_event(_gh("TileDepress"), e_)
                        self.pysweep.handle_event(_gh("TileChordDepress"), e_)

    def board_chord(self, hn, e):
        # Undepress currently depressed cells
        # Send out chord event
        self.board_undepress_tiles(True, e)
        width, height = self.gamedisplay.board_size
        if (0 <= e.col < width and 0 <= e.row < height):
            self.pysweep.handle_event(_gh("TileChord"), e)

    def board_undepress_tiles(self, chord, e_):
        # Helper function
        while self.depressed_tiles:
            e = BoardClick(e_.event, e_.time, *self.depressed_tiles.pop(), e_.lmb, e_.rmb)
            # e.row, e.col = self.depressed_tiles.pop()
            self.pysweep.handle_event(_gh("TileUndepress"), e)
            if chord:
                self.pysweep.handle_event(_gh("TileChordUndepress"), e)
            else:
                self.pysweep.handle_event(_gh("TileSingleUndepress"), e)

mods = {"GameDisplayManager": GameDisplayManager}
