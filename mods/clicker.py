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

            ("clicker", "LD"): [self.debug],
            ("clicker", "LM"): [self.debug],
            ("clicker", "LU"): [self.debug],
            ("clicker", "RD"): [self.debug],
            ("clicker", "RM"): [self.debug],
            ("clicker", "RU"): [self.debug],
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
        self.handle_event_with_flags(("clicker", "M"), e)
        if self.lmb > 0:
            self.handle_event_with_flags(("clicker", "LM"), e)
        if self.rmb > 0:
            self.handle_event_with_flags(("clicker", "RM"), e)


    # KEYBOARD
    def onpress_key(self, hn, e):
        if hasattr(e, "char") and e.char == self.keyboardsettings[0]:
            # LMB
            self.lmb += 2
            if self.lmb == 2:
                self.lmb_down(hn, e)
        elif hasattr(e, "char") and e.char == self.keyboardsettings[1]:
            # RMB
            self.rmb += 2
            if self.rmb == 2:
                self.rmb_down(hn, e)

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
            # LMB
            self.lmb -= 1
            if self.lmb == 0:
                self.lmb_up(hn, e)
        elif hasattr(e, "char") and e.char == self.keyboardsettings[1]:
            # RMB
            self.rmb -= 1
            if self.rmb == 0:
                self.rmb_up(hn, e)

    # MOUSE
    def onpress_mouse(self, hn, e, i):
        if i == self.mousesettings[0]:
            # LMB
            self.lmb += 1
            if self.lmb == 1:
                self.lmb_down(hn, e)
        elif i == self.mousesettings[1]:
            # RMB
            self.rmb += 1
            if self.rmb == 1:
                self.rmb_down(hn, e)

    def onrelease_mouse(self, hn, e, i):
        if i == self.mousesettings[0]:
            # LMB
            self.lmb -= 1
            if self.lmb == 0:
                self.lmb_up(hn, e)
        elif i == self.mousesettings[1]:
            # RMB
            self.rmb -= 1
            if self.rmb == 0:
                self.rmb_up(hn, e)

    # These functions are in charge of setting the right flags and sending the right events out

    def lmb_down(self, hn, e):
        self.handle_event_with_flags(("clicker", "LD"), e)
        self.handle_event_with_flags(("clicker", "D"), e)

    def rmb_down(self, hn, e):
        self.handle_event_with_flags(("clicker", "RD"), e)
        self.handle_event_with_flags(("clicker", "D"), e)

    def lmb_up(self, hn, e):
        self.handle_event_with_flags(("clicker", "LU"), e)
        self.handle_event_with_flags(("clicker", "U"), e)

    def rmb_up(self, hn, e):
        self.handle_event_with_flags(("clicker", "RU"), e)
        self.handle_event_with_flags(("clicker", "U"), e)

    def handle_event_with_flags(self, hn, e):
        e.widget = self.gamedisplay.display
        e.x, e.y = self.currentposition
        e.lmb = self.lmb
        e.rmb = self.rmb
        self.pysweep.handle_event(hn, e)

mods = {"Clicker": Clicker}
