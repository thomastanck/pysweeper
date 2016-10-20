class KeyboardClicker:
    hooks = {}
    required_events = [
        ("pysweep", "<KeyPress>"),
        ("pysweep", "<Motion>"),
        ("pysweep", "<KeyRelease>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<KeyPress>"):   [self.onpress],
            ("pysweep", "<Motion>"):     [self.onmove],
            ("pysweep", "<KeyRelease>"): [self.onrelease],
            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }
        # self.temporarily_down = []

        self.clicking = 0
        self.currentposition = (0,0)

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.mods["GameDisplay"]
        pass

    def onpress(self, hn, e):
        if hasattr(e, "char") and e.char == 'a':
            if self.clicking == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("pysweep", "<ButtonPress-1>"), e)

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
            e.widget = self.gamedisplay.display
            e.x, e.y = self.currentposition
            self.pysweep.handle_event(("pysweep", "<ButtonRelease-1>"), e)

    def onmove(self, hn, e):
        self.currentposition = (
            e.x + e.widget.winfo_rootx() - self.gamedisplay.display.winfo_rootx(),
            e.y + e.widget.winfo_rooty() - self.gamedisplay.display.winfo_rooty(),
        )
        e.widget = self.gamedisplay.display
        e.x, e.y = self.currentposition
        if self.clicking > 0:
            self.pysweep.handle_event(("pysweep", "<B1-Motion>"), e)

mods = {"KeyboardClicker": KeyboardClicker}
