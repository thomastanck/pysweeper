class Debugger:
    hooks = {}
    required_events = [
        ("pysweep", "<ButtonPress-1>"),
        ("pysweep", "<Motion>"),
        ("pysweep", "<Enter>"),
        ("pysweep", "<ButtonRelease-1>"),
        ("pysweep", "<KeyPress>"),
        ("pysweep", "<KeyRelease>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<ButtonPress-1>"):   [self.handlebuttonpress],
            ("pysweep", "<Motion>"):          [self.handlemotion],
            ("pysweep", "<Enter>"):           [self.handleenter],
            ("pysweep", "<ButtonRelease-1>"): [self.handlebuttonrelease],
            ("pysweep", "<KeyPress>"):        [self.handledown],
            ("pysweep", "<KeyRelease>"):      [self.handleup],
        }
        print("hi!")
    def handlebuttonpress(self, hn, e):
        print("OMG A BUTTON PRESS (at {}, {})".format(e.x, e.y))
    def handlebuttonrelease(self, hn, e):
        print("NO! COME BACK (at {}, {})".format(e.x, e.y))
    def handlemotion(self, hn, e):
        print("... (at {}, {})".format(e.x, e.y))
    def handleenter(self, hn, e):
        print("Enter: (at {}, {})".format(e.x, e.y))
        self.master.lift()
    def handledown(self, hn, e):
        print("down {}".format(e.keycode))
    def handleup(self, hn, e):
        print("up {}".format(e.keycode))

mods = {"Debugger": Debugger}
