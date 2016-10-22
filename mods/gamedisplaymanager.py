# Available hooks

# ("gamedisplaymanager", "TileClicked")
# Triggered when a player releases his mouse (thus clicking it) on top of a certain cell.

# ("gamedisplaymanager", "FaceClicked")
# Triggered when the player released his mouse on top of the face

# ("gamedisplaymanager", "MineCounterClicked")
# ("gamedisplaymanager", "TimerClicked")
# Similar

# ("gamedisplaymanager", "PanelClicked")
# ("gamedisplaymanager", "DisplayClicked")
# If none of the above were triggered, this is triggered (depending on whether the mouse was on the panel or on the borders)


class GameDisplayManager:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("clicker", "LD"): [self.handle_mouse_event],
            ("clicker", "LM"): [self.handle_mouse_event],
            ("clicker", "LU"): [self.handle_mouse_event],
            ("clicker", "RD"): [self.handle_mouse_event],
            ("clicker", "RM"): [self.handle_mouse_event],
            ("clicker", "RU"): [self.handle_mouse_event],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

        self.temporarily_down = []
        self.current_widget_handler = None
        self.mousedown = False

        self.chording_mode = 0
        # 0: didn't double click during this press (either LMB down, LMB up, or RMB down, RMB up)
        # 1: did double click at some point during the click (LMB down, RMB down, *flag on*, RMB up, RMB down, LMB up, RMB up, *flag off*)

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.mods["GameDisplay"]

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
                if self.current_widget_handler and handler != self.current_widget_handler[1]:
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

    def handle_board(self, hn, e):
        LD = ("clicker", "LD")
        LM = ("clicker", "LM")
        LU = ("clicker", "LU")
        RD = ("clicker", "RD")
        RM = ("clicker", "RM")
        RU = ("clicker", "RU")
        # As these are more complicated, we split them up.

        # We go into chording mode before handling the event
        # But we leave chording mode only after the event
        if e.lmb > 0 and e.rmb > 0:
            # both buttons down means go into chording mode
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
        face_button = self.gamedisplay.face_button
        if e.inbounds:
            if hn[1] == "LD" or hn[1] == "LM":
                face_button.set_face("pressed")
            elif hn[1] == "LU":
                self.pysweep.handle_event(("gamedisplaymanager", "FaceClicked"), e)
                face_button.set_face("happy")
        else:
            face_button.set_face("happy")

    # Click only handlers
    def handle_mine(self, hn, e):
        if hn[1] == "LU":
            self.pysweep.handle_event(("gamedisplaymanager", "MineCounterClicked"), e)
    def handle_timer(self, hn, e):
        if hn[1] == "LU":
            self.pysweep.handle_event(("gamedisplaymanager", "TimerClicked"), e)
    def handle_panel(self, hn, e):
        if hn[1] == "LU":
            self.pysweep.handle_event(("gamedisplaymanager", "PanelClicked"), e)
    def handle_display(self, hn, e):
        if hn[1] == "LU":
            self.pysweep.handle_event(("gamedisplaymanager", "DisplayClicked"), e)


    # Board events
    def board_depress(self, hn, e):
        # Undepress currently depressed cells
        # Depress current cell
        col = e.x // 16
        row = e.y // 16
        width, height = self.gamedisplay.size
        if not (0 <= col < width and 0 <= row < height):
            # i.e., we've moved off the board
            self.board_reset_depressed()
        else:
            self.board_reset_depressed(row, col)
            if self.gamedisplay.get_tile_type(row, col) == "unopened":
                self.temporarily_down.append((row, col))
                self.gamedisplay.set_tile(row, col, "tile_0")

    def board_open(self, hn, e):
        # Undepress currently depressed cells
        # Send out click event
        col = e.x // 16
        row = e.y // 16
        if (col, row) in self.temporarily_down:
            self.temporarily_down.remove((col,row))
        self.board_reset_depressed()
        width, height = self.gamedisplay.size
        if (0 <= col < width and 0 <= row < height):
            e.row, e.col = row, col
            self.pysweep.handle_event(("gamedisplaymanager", "TileClicked"), e)

    def board_toggle_flag(self, hn, e):
        # Send out click event
        col = e.x // 16
        row = e.y // 16
        width, height = self.gamedisplay.size
        if (0 <= col < width and 0 <= row < height):
            e.row, e.col = row, col
            self.pysweep.handle_event(("gamedisplaymanager", "TileRightClicked"), e)

    def board_depress_chord(self, hn, e):
        # Undepress currently depressed cells
        # Depress current cell and neighbours
        col = e.x // 16
        row = e.y // 16
        width, height = self.gamedisplay.size
        self.board_reset_depressed()
        for drow in range(-1, 2):
            for dcol in range(-1, 2):
                row_, col_ = row+drow, col+dcol
                if (0 <= col_ < width and 0 <= row_ < height):
                    if self.gamedisplay.get_tile_type(row_, col_) == "unopened":
                        self.temporarily_down.append((row_, col_))
                        self.gamedisplay.set_tile(row_, col_, "tile_0")

    def board_chord(self, hn, e):
        # Undepress currently depressed cells
        # Send out chord event
        col = e.x // 16
        row = e.y // 16
        self.board_reset_depressed()
        width, height = self.gamedisplay.size
        if (0 <= col < width and 0 <= row < height):
            e.row, e.col = row, col
            self.pysweep.handle_event(("gamedisplaymanager", "TileChorded"), e)

    def board_reset_depressed(self, avoid_x=-1, avoid_y=-1):
        # Helper function
        add_back = (avoid_x, avoid_y) in self.temporarily_down
        if add_back:
            self.temporarily_down.remove((avoid_x, avoid_y))
        while self.temporarily_down:
            x, y = self.temporarily_down.pop()
            self.gamedisplay.set_tile(x, y, "unopened")
        if add_back:
            self.temporarily_down.append((avoid_x, avoid_y))

mods = {"GameDisplayManager": GameDisplayManager}
