class KeyboardClicker:
    hooks = {}
    required_events = [
        ("pysweep3", "<KeyPress>"),
        ("pysweep3", "<Motion>"),
        ("pysweep3", "<KeyRelease>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            ("pysweep3", "<KeyPress>"):   [self.onpress],
            ("pysweep3", "<Motion>"):     [self.onmove],
            ("pysweep3", "<KeyRelease>"): [self.onrelease],
            ("pysweep3", "AllModsLoaded"): [self.modsloaded],
        }
        self.temporarily_down = []

        self.clicking = 0
        self.currentposition = (0,0)

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep3.mods["GameDisplay"]
        pass

    def onpress(self, hn, e):
        if hasattr(e, "char") and e.char == 'a':
            if self.clicking == 0:
                e.x, e.y = self.currentposition
                e.col, e.row = e.x//16, e.y//16
                self.pysweep3.handle_event(("board", "<ButtonPress-1>"), e)

            if self.clicking < 2:
                print("Keyboard Click!")
                self.clicking = 2

    def onrelease(self, hn, e):
        if hasattr(e, "char") and e.char == 'a':
            self.clicking = 1
            self.master.after(0, self.actuallyrelease, hn, e)

    def actuallyrelease(self, hn, e):
        if self.clicking == 1:
            self.clicking = 0
            e.x, e.y = self.currentposition
            e.col, e.row = e.x//16, e.y//16
            self.pysweep3.handle_event(("board", "<ButtonRelease-1>"), e)

    def onmove(self, hn, e):
        self.currentposition = (
            e.x + e.widget.winfo_rootx() - self.gamedisplay.display.board.winfo_rootx(),
            e.y + e.widget.winfo_rooty() - self.gamedisplay.display.board.winfo_rooty(),
        )
        e.x, e.y = self.currentposition
        if self.clicking > 0:
            e.col, e.row = e.x//16, e.y//16
            self.pysweep3.handle_event(("board", "<B1-Motion>"), e)

mods = {"KeyboardClicker": KeyboardClicker}
