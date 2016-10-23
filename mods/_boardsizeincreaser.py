class BoardSizeIncreaser:
    hooks = {}
    required_events = [("pysweep", "<KeyPress>")]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<KeyPress>"): [self.increaseboardsize],
            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

        self.temporarily_down = []

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.gamedisplay

    def increaseboardsize(self, hn, e):
        width, height = self.gamedisplay.size
        width += 1
        self.gamedisplay.set_size(width, height)

mods = {"BoardSizeIncreaser": BoardSizeIncreaser}
