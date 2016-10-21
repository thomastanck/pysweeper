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
            ("clicker", "LU"):   [self.handle_mouse_event],
            ("clicker", "RD"): [self.handle_mouse_event],
            ("clicker", "RM"): [self.handle_mouse_event],
            ("clicker", "RU"):   [self.handle_mouse_event],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

        self.temporarily_down = []
        self.current_widget_handler = None
        self.mousedown = False

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.mods["GameDisplay"]

    # Getters for various widgets
    def get_display(self):
        return self.gamedisplay.display
    def get_board(self):
        return self.gamedisplay.display.board
    def get_panel(self):
        return self.gamedisplay.display.panel
    def get_face_button(self):
        return self.gamedisplay.display.panel.face_button
    def get_mine_counter(self):
        return self.gamedisplay.display.panel.mine_counter
    def get_timer(self):
        return self.gamedisplay.display.panel.timer

    # Get size
    def get_size(self):
        return self.gamedisplay.size

    # Face button setters
    def set_face_happy(self):
        self.get_face_button().set_face("happy")
    def set_face_pressed(self):
        self.get_face_button().set_face("pressed")
    def set_face_blast(self):
        self.get_face_button().set_face("blast")
    def set_face_cool(self):
        self.get_face_button().set_face("cool")

    # Tile getters
    def get_tile_type(self, row, col):
        board = self.gamedisplay.display.board
        return board.get_tile_type(row, col)
    def get_tile_number(self, row, col):
        board = self.gamedisplay.display.board
        return int(board.get_tile_type(row, col)[-1:]) # get the last char and convert to int

    # Tile setters
    def set_tile_mine(self, row, col):
        self.set_tile(row, col, "mine")
    def set_tile_blast(self, row, col):
        self.set_tile(row, col, "blast")
    def set_tile_flag(self, row, col):
        self.set_tile(row, col, "flag")
    def set_tile_flag_wrong(self, row, col):
        self.set_tile(row, col, "flag_wrong")
    def set_tile_unopened(self, row, col):
        self.set_tile(row, col, "unopened")
    def set_tile_number(self, row, col, number):
        # number: 0..8
        if 0 <= number and number < 9:
            self.set_tile(row, col, "tile_{}".format(number))
        else:
            raise ValueError('Tile number {} does not exist'.format(number))
    def set_tile(self, i, j, tile_type):
        board = self.gamedisplay.display.board
        board.draw_tile(i, j, tile_type)

    def reset_board(self):
        # reset the board to all unopened
        board = self.gamedisplay.display.board

        width = board.board_width
        height = board.board_height

        for row in range(height):
            for col in range(width):
                self.set_tile_unopened(row, col)



    def handle_mouse_event(self, hn, e):
        # Other mods should call pysweep.mods["GameDisplayManager"].handle_mouse_event(hn, e)
        # when they receive button events (<ButtonPress-1>, <B1-Motion>, and <ButtonRelease-1>)
        # if hn[0] != "pysweep":
        #     raise ValueError("GameDisplayManager handles pysweep events! (not board or gamedisplay events)")
        widget_handlers = [
            (self.gamedisplay.display.board,              self.handle_board),
            (self.gamedisplay.display.panel.face_button,  self.handle_face),
            (self.gamedisplay.display.panel.mine_counter, self.handle_mine),
            (self.gamedisplay.display.panel.timer,        self.handle_timer),
            (self.gamedisplay.display.panel,              self.handle_panel),
            (self.gamedisplay.display,                    self.handle_display),
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
        # As these are more complicated, we split them up.
        if hn[1] == "LD" or hn[1] == "LM":
            self.board_press_lmb(hn, e)
        elif hn[1] == "LU":
            self.board_release_lmb(hn, e)
        elif hn[1] == "RD" or hn[1] == "RM":
            self.board_press_rmb(hn, e)
        elif hn[1] == "RU":
            self.board_release_rmb(hn, e)

    def handle_face(self, hn, e):
        face_button = self.gamedisplay.display.panel.face_button
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



    def board_press_lmb(self, hn, e):
        board = self.gamedisplay.display.board

        col = e.x // 16
        row = e.y // 16
        width, height = board.board_width, board.board_height
        if not (0 <= col < width and 0 <= row < height):
            # i.e., we've moved off the board
            self.board_reset_depressed()
        else:
            self.board_reset_depressed(row, col)
            if self.get_tile_type(row, col) == "unopened":
                self.temporarily_down.append((row, col))
                self.set_tile(row, col, "tile_0")

    def board_release_lmb(self, hn, e):
        board = self.gamedisplay.display.board

        col = e.x // 16
        row = e.y // 16
        if (col, row) in self.temporarily_down:
            self.temporarily_down.remove((col,row))
        self.board_reset_depressed()
        width = board.board_width
        height = board.board_height
        if (0 <= col < width and 0 <= row < height):
            e.row, e.col = row, col
            self.pysweep.handle_event(("gamedisplaymanager", "TileClicked"), e)

    def board_press_rmb(self, hn, e):
        pass

    def board_release_rmb(self, hn, e):
        board = self.gamedisplay.display.board
        col = e.x // 16
        row = e.y // 16
        width = board.board_width
        height = board.board_height
        if (0 <= col < width and 0 <= row < height):
            e.row, e.col = row, col
            self.pysweep.handle_event(("gamedisplaymanager", "TileRightClicked"), e)

    def board_reset_depressed(self, avoid_x=-1, avoid_y=-1):
        add_back = (avoid_x, avoid_y) in self.temporarily_down
        if add_back:
            self.temporarily_down.remove((avoid_x, avoid_y))
        while self.temporarily_down:
            x, y = self.temporarily_down.pop()
            self.set_tile(x, y, "unopened")
        if add_back:
            self.temporarily_down.append((avoid_x, avoid_y))

mods = {"GameDisplayManager": GameDisplayManager}
