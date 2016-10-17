class WindowCloser:
    hooks = {}
    required_events = []
    required_protocols = [("pysweep3", "WM_DELETE_WINDOW")]

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            "pysweep3WM_DELETE_WINDOW": [self.on_close],
        }

    def on_close(self, hn, e):
        self.pysweep3.handle_event("pysweep3BEFORE_WM_DELETE_WINDOW", None)
        self.master.destroy()
