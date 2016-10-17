class GameDisplayDefaultTimer:
    hooks = {}
    required_events = [
        ("pysweep3", "<ButtonPress-1>"),
        ("pysweep3", "<ButtonRelease-1>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            "pysweep3<ButtonPress-1>":   [self.onpress],
            "pysweep3<ButtonRelease-1>": [self.onrelease],
            "AllModsLoaded": [self.modsloaded],
        }

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep3.mods["GameDisplay"]
        self.timermod = self.pysweep3.mods["Timer"]
        self.timer = self.timermod.get_timer(self.timercallback)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.display.set_timer(int(elapsed))

    def onpress(self, hn, e):
        self.timer.start_timer()

    def onrelease(self, hn, e):
        self.timer.stop_timer()

mods = {"GameDisplayDefaultTimer": GameDisplayDefaultTimer}
