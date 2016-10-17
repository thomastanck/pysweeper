class GameDisplayDefaultClick:
    hooks = {}
    required_events = [
        ("board", "<ButtonPress-1>"),
        ("board", "<B1-Motion>"),
        ("board", "<ButtonRelease-1>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            "board<ButtonPress-1>":   [self.onpress],
            "board<B1-Motion>":       [self.onmove],
            "board<ButtonRelease-1>": [self.onrelease],
            "AllModsLoaded": [self.modsloaded],
        }
        self.temporarily_down = []

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep3.mods["GameDisplay"]

    def get_tile_type(self, i, j):
        board = self.gamedisplay.board
        return board.get_tile_type(i, j)

    def set_tile(self, i, j, tile_type):
        board = self.gamedisplay.board
        board.set_tile(i, j, tile_type)

    def reset_depressed(self, avoid_x=-1, avoid_y=-1):
        add_back = (avoid_x, avoid_y) in self.temporarily_down
        if add_back:
            self.temporarily_down.remove((avoid_x, avoid_y))
        while self.temporarily_down:
            x, y = self.temporarily_down.pop()
            self.set_tile(x, y, "unopened")
        if add_back:
            self.temporarily_down.append((avoid_x, avoid_y))

    def onpress(self, hn, e):
        board = self.gamedisplay.board

        col = e.col
        row = e.row
        width, height = board.board_width, board.board_height
        if not (0 <= col < width and 0 <= row < height):
            # i.e., we've moved off the board
            self.reset_depressed()
        else:
            # tile = self.tiles[row][col]
            self.reset_depressed(row, col)
            if self.get_tile_type(row, col) == "unopened":
                self.temporarily_down.append((row, col))
                self.set_tile(row, col, "tile_0")

    def onmove(self, hn, e):
        self.onpress(hn, e)

    def onrelease(self, hn, e):
        self.gamedisplay = self.pysweep3.mods["GameDisplay"]
        board = self.gamedisplay.board

        col = e.col
        row = e.row
        if (col, row) in self.temporarily_down:
            self.temporarily_down.remove((col,row))
        self.reset_depressed()
        width = board.board_width
        height = board.board_height
        if (0 <= col < width and 0 <= row < height):
            self.set_tile(row, col, "tile_0")

mods = {"GameDisplayDefaultClick": GameDisplayDefaultClick}
