import platform

class Clicker:
    hooks = {}
    required_events = [
        ("pysweep", "<KeyPress>"),
        ("pysweep", "<Motion>"),
        ("pysweep", "<KeyRelease>"),

        ("pysweep", "<ButtonPress-1>"),
        ("pysweep", "<ButtonRelease-1>"),

        ("pysweep", "<ButtonPress-2>"),
        ("pysweep", "<ButtonRelease-2>"),

        ("pysweep", "<ButtonPress-3>"),
        ("pysweep", "<ButtonRelease-3>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "<Motion>"):     [self.onmove],
            ("pysweep", "<B1-Motion>"):  [self.onmove],
            ("pysweep", "<B2-Motion>"):  [self.onmove],
            ("pysweep", "<B3-Motion>"):  [self.onmove],

            ("pysweep", "<KeyPress>"):   [self.onpress_key],
            ("pysweep", "<KeyRelease>"): [self.onrelease_key],

            ("pysweep", "<ButtonPress-1>"):   [lambda hn, e, i=1: self.onpress_mouse(hn, e, i)],
            ("pysweep", "<ButtonRelease-1>"): [lambda hn, e, i=1: self.onrelease_mouse(hn, e, i)],

            ("pysweep", "<ButtonPress-2>"):   [lambda hn, e, i=2: self.onpress_mouse(hn, e, i)],
            ("pysweep", "<ButtonRelease-2>"): [lambda hn, e, i=2: self.onrelease_mouse(hn, e, i)],

            ("pysweep", "<ButtonPress-3>"):   [lambda hn, e, i=3: self.onpress_mouse(hn, e, i)],
            ("pysweep", "<ButtonRelease-3>"): [lambda hn, e, i=3: self.onrelease_mouse(hn, e, i)],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],

            ("clicker", "LMBDown"): [self.debug],
            ("clicker", "LMBMove"): [self.debug],
            ("clicker", "LMBUp"):   [self.debug],
            ("clicker", "RMBDown"): [self.debug],
            ("clicker", "RMBMove"): [self.debug],
            ("clicker", "RMBUp"):   [self.debug],
        }

        # settings = [LMB key/mouse button, RMB key/mouse button]
        if platform.system() == 'Darwin':  # How Mac OS X is identified by Python
            self.keyboardsettings = ["1", "2"]
            self.mousesettings =    [1, 2] # OSX uses mouse button 2 for right click. weird huh?
        else:
            self.keyboardsettings = ["1", "2"]
            self.mousesettings =    [1, 3] # Everyone else uses mouse button 3 for right click.

        # Every additional key that matches increases this counter by one
        # Keyboard keys increase this counter by two, but decrease it once when
        # a release is detected and another time on the next tkinter tick (like a bouncer)
        # to avoid key repetition behaviour
        self.lmb = 0
        self.rmb = 0
        self.currentposition = (0, 0)

    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.mods["GameDisplay"]
        pass

    def debug(self, hn, e):
        # print(hn)
        return

    # POSITION
    def onmove(self, hn, e):
        self.currentposition = (
            e.x + e.widget.winfo_rootx() - self.gamedisplay.display.winfo_rootx(),
            e.y + e.widget.winfo_rooty() - self.gamedisplay.display.winfo_rooty(),
        )
        e.widget = self.gamedisplay.display
        e.x, e.y = self.currentposition
        e.lmb = self.lmb > 0
        e.rmb = self.rmb > 0
        self.pysweep.handle_event(("clicker", "Move"), e)
        if self.lmb > 0:
            self.pysweep.handle_event(("clicker", "LMBMove"), e)
        if self.rmb > 0:
            self.pysweep.handle_event(("clicker", "RMBMove"), e)


    # KEYBOARD
    def onpress_key(self, hn, e):
        if hasattr(e, "char") and e.char == self.keyboardsettings[0]:
            # LMB
            if self.lmb == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("clicker", "LMBDown"), e)
            self.lmb += 2
        elif hasattr(e, "char") and e.char == self.keyboardsettings[1]:
            # RMB
            if self.rmb == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("clicker", "RMBDown"), e)
            self.rmb += 2

    def onrelease_key(self, hn, e):
        if hasattr(e, "char") and e.char == self.keyboardsettings[0]:
            # LMB
            self.lmb -= 1
            self.master.after(0, self.actuallyrelease, hn, e)
        elif hasattr(e, "char") and e.char == self.keyboardsettings[1]:
            # RMB
            self.rmb -= 1
            self.master.after(0, self.actuallyrelease, hn, e)

    def actuallyrelease(self, hn, e):
        if hasattr(e, "char") and e.char == self.keyboardsettings[0]:
            self.lmb -= 1
            if self.lmb == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("clicker", "LMBUp"), e)
        elif hasattr(e, "char") and e.char == self.keyboardsettings[1]:
            self.rmb -= 1
            if self.rmb == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("clicker", "RMBUp"), e)

    # MOUSE
    def onpress_mouse(self, hn, e, i):
        if i == self.mousesettings[0]:
            # LMB
            if self.lmb == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("clicker", "LMBDown"), e)
            self.lmb += 1
        elif i == self.mousesettings[1]:
            # RMB
            if self.rmb == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("clicker", "RMBDown"), e)
            self.rmb += 1

    def onrelease_mouse(self, hn, e, i):
        if i == self.mousesettings[0]:
            # LMB
            self.lmb -= 1
            if self.lmb == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("clicker", "LMBUp"), e)
        elif i == self.mousesettings[1]:
            # RMB
            self.rmb -= 1
            if self.rmb == 0:
                e.widget = self.gamedisplay.display
                e.x, e.y = self.currentposition
                self.pysweep.handle_event(("clicker", "RMBUp"), e)

mods = {"Clicker": Clicker}
