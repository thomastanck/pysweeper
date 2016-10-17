class Debugger:
    hooks = {}
    required_events = [
        ("pysweep3", "<ButtonPress-1>"),
        ("pysweep3", "<Motion>"),
        ("pysweep3", "<Enter>"),
        ("pysweep3", "<ButtonRelease-1>"),
        ("pysweep3", "<KeyPress>"),
        ("pysweep3", "<KeyRelease>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            "pysweep3<ButtonPress-1>":   [self.handlebuttonpress],
            "pysweep3<Motion>":          [self.handlemotion],
            "pysweep3<Enter>":           [self.handleenter],
            "pysweep3<ButtonRelease-1>": [self.handlebuttonrelease],
            "pysweep3<KeyPress>":        [self.handledown],
            "pysweep3<KeyRelease>":      [self.handleup],
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

