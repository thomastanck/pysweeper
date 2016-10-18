class GameDisplayDefaultTimer:
    hooks = {}
    required_events = [
        ("pysweep", "<ButtonPress-1>"),
        ("pysweep", "<ButtonRelease-1>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<ButtonPress-1>"):   [self.onpress],
            ("pysweep", "<ButtonRelease-1>"): [self.onrelease],
            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.mods["GameDisplay"]
        self.timermod = self.pysweep.mods["Timer"]
        self.timer = self.timermod.get_timer(self.timercallback)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.display.set_timer(int(elapsed))

    def onpress(self, hn, e):
        self.timer.start_timer()

    def onrelease(self, hn, e):
        self.timer.stop_timer()

mods = {"GameDisplayDefaultTimer": GameDisplayDefaultTimer}
