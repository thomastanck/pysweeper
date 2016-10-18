# Available hooks

# ("boardmanager", "TileClicked")
# Triggered when a player releases his mouse (thus clicking it) on top of a certain cell.

class BoardManager:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

        self.temporarily_down = []

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.mods["GameDisplay"]

    def handle_mouse_event(self, hn, e):
        # Other mods should call pysweep.mods["BoardManager"].handle_mouse_event(hn, e)
        # when they receive button events (<ButtonPress-1>, <B1-Motion>, and <ButtonRelease-1>)
        if hn[1] == "<ButtonPress-1>":
            self.onpress(hn, e)
        elif hn[1] == "<B1-Motion>":
            self.onmove(hn, e)
        elif hn[1] == "<ButtonRelease-1>":
            self.onrelease(hn, e)

    def set_tile_number(self, row, col, number):
        # number: 0..8
        if 0 <= number and number < 9:
            self.set_tile(row, col, "tile_{}".format(number))
        else:
            raise ValueError('Tile number {} does not exist'.format(number))

    def set_tile_unopened(self, row, col):
        self.set_tile(row, col, "unopened")

    def get_tile_type(self, i, j):
        board = self.gamedisplay.display.board
        return board.get_tile_type(i, j)

    def set_tile(self, i, j, tile_type):
        board = self.gamedisplay.display.board
        board.set_tile(i, j, tile_type)

    def reset_board(self):
        # reset the board to all unopened
        board = self.gamedisplay.display.board

        width = board.board_width
        height = board.board_height

        for row in range(height):
            for col in range(width):
                self.set_tile_unopened(row, col)



    def onpress(self, hn, e):
        board = self.gamedisplay.display.board

        col = e.x // 16
        row = e.y // 16
        width, height = board.board_width, board.board_height
        if not (0 <= col < width and 0 <= row < height):
            # i.e., we've moved off the board
            self.reset_depressed()
        else:
            self.reset_depressed(row, col)
            if self.get_tile_type(row, col) == "unopened":
                self.temporarily_down.append((row, col))
                self.set_tile(row, col, "tile_0")

    def onmove(self, hn, e):
        self.onpress(hn, e)

    def onrelease(self, hn, e):
        board = self.gamedisplay.display.board

        col = e.x // 16
        row = e.y // 16
        if (col, row) in self.temporarily_down:
            self.temporarily_down.remove((col,row))
        self.reset_depressed()
        width = board.board_width
        height = board.board_height
        if (0 <= col < width and 0 <= row < height):
            e.row, e.col = row, col
            self.pysweep.handle_event(("boardmanager", "TileClicked"), e)

    def reset_depressed(self, avoid_x=-1, avoid_y=-1):
        add_back = (avoid_x, avoid_y) in self.temporarily_down
        if add_back:
            self.temporarily_down.remove((avoid_x, avoid_y))
        while self.temporarily_down:
            x, y = self.temporarily_down.pop()
            self.set_tile(x, y, "unopened")
        if add_back:
            self.temporarily_down.append((avoid_x, avoid_y))

mods = {"BoardManager": BoardManager}
