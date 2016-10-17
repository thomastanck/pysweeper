class BoardSizeIncreaser:
    hooks = {}
    required_events = [("pysweep3", "<KeyPress>")]
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            "pysweep3<KeyPress>": [self.increaseboardsize],
            "AllModsLoaded": [self.modsloaded],
        }

        self.temporarily_down = []

    def modsloaded(self, e):
        self.gamedisplay = self.pysweep3.mods["GameDisplay"]

    def increaseboardsize(self, e):
        width, height = self.gamedisplay.size
        width += 1
        self.gamedisplay.set_size(width, height)
