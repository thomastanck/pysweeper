class Debugger:
    hooks = {}
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
    def handlebuttonpress(self, e):
        print("OMG A BUTTON PRESS (at {}, {})".format(e.x, e.y))
    def handlebuttonrelease(self, e):
        print("NO! COME BACK (at {}, {})".format(e.x, e.y))
    def handlemotion(self, e):
        print("... (at {}, {})".format(e.x, e.y))
    def handleenter(self, e):
        print("Enter: (at {}, {})".format(e.x, e.y))
        self.master.lift()
    def handledown(self, e):
        print("down {}".format(e.keycode))
    def handleup(self, e):
        print("up {}".format(e.keycode))

