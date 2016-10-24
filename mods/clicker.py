import platform

import time

class ClickerEvent:
    # Stripped down version of the tkinter event, and adds some restrictions so it'll be easier to debug in the future
    # One motivation for the attribute restrictions is that we frequently compute row/col out of x/y.
    # In order to prevent mixing up events which are supposed to have x/y and events which are supposed to have row/col,
    # we'll simply force ClickerEvent to use x/y only, then compute row/col using another class that only has row/col.
    __isfrozen = False
    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError( "%r is a frozen class, cannot set %s" % (self, key))
        object.__setattr__(self, key, value)

    def __init__(self, widget, event=None, time=0, x=0, y=0, lmb=False, rmb=False, inbounds=False):
        self.widget = widget
        self.event = event # "LD", "LU", "M", etc.
        self.time = time
        self.x = x
        self.y = y
        self.lmb = lmb
        self.rmb = rmb
        self.inbounds = inbounds
        self.__isfrozen = True

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

            ("clicker", "D"): [self.debug],
            ("clicker", "M"): [self.debug],
            ("clicker", "U"): [self.debug],
            ("clicker", "LD"): [self.debug],
            ("clicker", "LM"): [self.debug],
            ("clicker", "LU"): [self.debug],
            ("clicker", "RD"): [self.debug],
            ("clicker", "RM"): [self.debug],
            ("clicker", "RU"): [self.debug],
        }

        # settings = [LMB key/mouse button, RMB key/mouse button]
        if platform.system() == 'Darwin':  # How Mac OS X is identified by Python
            self.keyboardsettings = ["3", "2"]
            self.mousesettings =    [1, 2] # OSX uses mouse button 2 for right click. weird huh?
        else:
            self.keyboardsettings = ["3", "2"]
            self.mousesettings =    [1, 3] # Everyone else uses mouse button 3 for right click.

        # Every additional key that matches increases this counter by one
        # Keyboard keys increase this counter by two, but decrease it once when
        # a release is detected and another time on the next tkinter tick (like a bouncer)
        # to avoid key repetition behaviour
        self.mouse_lmb = 0
        self.mouse_rmb = 0
        self.key_lmb = 0
        self.key_rmb = 0
        self.currentposition = (0, 0)

    @property
    def lmb(self):
        return self.mouse_lmb + self.key_lmb
    @property
    def rmb(self):
        return self.mouse_rmb + self.key_rmb


    def modsloaded(self, hn, e):
        self.gamedisplay = self.pysweep.gamedisplay
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
        e.lmb = (self.mouse_lmb + self.key_lmb) > 0
        e.rmb = (self.mouse_rmb + self.key_rmb) > 0
        self.send_event(("clicker", "M"), e)
        if e.lmb > 0:
            self.send_event(("clicker", "LM"), e)
        if e.rmb > 0:
            self.send_event(("clicker", "RM"), e)


    # KEYBOARD
    def onpress_key(self, hn, e):
        if hasattr(e, "char") and e.char == self.keyboardsettings[0]:
            # LMB
            if (self.mouse_lmb + self.key_lmb) == 0:
                self.key_lmb = 2
                self.lmb_down(hn, e)
            else:
                self.key_lmb = 2
        elif hasattr(e, "char") and e.char == self.keyboardsettings[1]:
            # RMB
            if (self.mouse_rmb + self.key_rmb) == 0:
                self.key_rmb = 2
                self.rmb_down(hn, e)
            else:
                self.key_rmb = 2

    def onrelease_key(self, hn, e):
        if hasattr(e, "char") and e.char == self.keyboardsettings[0]:
            # LMB
            self.key_lmb = 1
            self.master.after(0, self.actuallyrelease, hn, e)
        elif hasattr(e, "char") and e.char == self.keyboardsettings[1]:
            # RMB
            self.key_rmb = 1
            self.master.after(0, self.actuallyrelease, hn, e)

    def actuallyrelease(self, hn, e):
        if hasattr(e, "char") and e.char == self.keyboardsettings[0]:
            # LMB
            if self.key_lmb == 1:
                self.key_lmb = 0
                if (self.mouse_lmb + self.key_lmb) == 0:
                    self.lmb_up(hn, e)
        elif hasattr(e, "char") and e.char == self.keyboardsettings[1]:
            # RMB
            if self.key_rmb == 1:
                self.key_rmb = 0
                if (self.mouse_rmb + self.key_rmb) == 0:
                    self.rmb_up(hn, e)

    # MOUSE
    def onpress_mouse(self, hn, e, i):
        if i == self.mousesettings[0]:
            # LMB
            if (self.mouse_lmb + self.key_lmb) == 0:
                self.mouse_lmb = 1
                self.lmb_down(hn, e)
            else:
                self.mouse_lmb = 1
        elif i == self.mousesettings[1]:
            # RMB
            if (self.mouse_rmb + self.key_rmb) == 0:
                self.mouse_rmb = 1
                self.rmb_down(hn, e)
            else:
                self.mouse_rmb = 1

    def onrelease_mouse(self, hn, e, i):
        if i == self.mousesettings[0]:
            # LMB
            self.mouse_lmb = 0
            if (self.mouse_lmb + self.key_lmb) == 0:
                self.lmb_up(hn, e)
        elif i == self.mousesettings[1]:
            # RMB
            self.mouse_rmb = 0
            if (self.mouse_rmb + self.key_rmb) == 0:
                self.rmb_up(hn, e)

    # These functions are in charge of setting the right flags and sending the right events out

    def lmb_down(self, hn, e):
        self.send_event(("clicker", "LD"), e)
        self.send_event(("clicker", "D"), e)

    def rmb_down(self, hn, e):
        self.send_event(("clicker", "RD"), e)
        self.send_event(("clicker", "D"), e)

    def lmb_up(self, hn, e):
        self.send_event(("clicker", "LU"), e)
        self.send_event(("clicker", "U"), e)

    def rmb_up(self, hn, e):
        self.send_event(("clicker", "RU"), e)
        self.send_event(("clicker", "U"), e)

    def send_event(self, hn, e):
        e = ClickerEvent(self.gamedisplay.display, hn[1], time.time(), self.currentposition[0], self.currentposition[1], self.lmb, self.rmb)
        # e.widget = self.gamedisplay.display
        # e.x, e.y = self.currentposition
        # e.lmb = self.lmb
        # e.rmb = self.rmb
        self.pysweep.handle_event(hn, e)

mods = {"Clicker": Clicker}
