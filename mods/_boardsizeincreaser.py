class BoardSizeIncreaser:
    hooks = {}
    required_events = [("pysweep3", "<KeyPress>")]
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            ("pysweep3", "<KeyPress>"): [self.increaseboardsize],
            ("pysweep3", "AllModsLoaded"): [self.modsloaded],
        }

        self.temporarily_down = []

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep3.mods["GameDisplay"]

    def increaseboardsize(self, hn, e):
        width, height = self.gamedisplay.size
        width += 1
        self.gamedisplay.set_size(width, height)

mods = {"BoardSizeIncreaser": BoardSizeIncreaser}
