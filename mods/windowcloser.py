class WindowCloser:
    hooks = {}
    required_events = []
    required_protocols = [("pysweep", "WM_DELETE_WINDOW")]

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "WM_DELETE_WINDOW"): [self.on_close],
        }

    def on_close(self, hn, e):
        self.pysweep.handle_event(("windowcloser", "BEFORE_CLOSE"), None)
        self.master.destroy()

mods = {"WindowCloser": WindowCloser}
