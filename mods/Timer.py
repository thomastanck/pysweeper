import threading, time

class Timer:
    hooks = {}
    required_events = []
    required_protocols = []
    # required_protocols = ["WM_DELETE_WINDOW"] # We depend on WindowCloser mod to trigger the pysweep3BEFOREWM_DELETE_WINDOW hook

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3
        self.hooks = {
            "pysweep3BEFORE_WM_DELETE_WINDOW": [self.on_close],
        }
        # This mod is pretty benign and doesn't do much except give other mods TimerObj's
        self.timers = [] # A list of timers it has made
        # self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_timer(self, callback):
        timerobj = TimerObj(callback)
        self.timers.append(timerobj)
        return timerobj

    def on_close(self, e):
        for timer in self.timers:
            timer.kill_timer()

class TimerObj:
    def __init__(self, callback, resolution=1):
        # calls callback whenever the time changes more than resolution (which will be every second by default)
        self.callback = callback
        self.resolution = resolution
        self.start_time = 0
        self.current_time = 0
        self.stop_time = 0
        self.timing_mode = False
        self.timer_threads = []

    def timer_thread(self):
        while self.timing_mode:
            curtime = time.time()
            elapsed = curtime - self.start_time
            sincelasttick = curtime - self.current_time
            self.current_time = curtime
            if elapsed > self.resolution:
                self.callback(elapsed, sincelasttick)
            time.sleep(self.resolution / 100)

    def start_timer(self):
        self.start_time = time.time()
        self.current_time = self.start_time
        self.timing_mode = True

        new_thread = threading.Thread(target=self.timer_thread)
        self.timer_threads.append(new_thread)
        new_thread.start()

        self.callback(0, 0)

    def stop_timer(self):
        if not self.timing_mode:
            return # Do nothing if already stopped
        self.stop_time = time.time()
        self.timing_mode = False

        curtime = time.time()
        elapsed = curtime - self.start_time
        sincelasttick = curtime - self.current_time
        self.current_time = curtime
        self.stop_time = curtime

        self.callback(elapsed, sincelasttick)

        threads_to_remove = []
        for timer_thread in self.timer_threads:
            if not timer_thread.is_alive():
                threads_to_remove.append(timer_thread)
        # print("Threads to remove:", threads_to_remove)
        for thread in threads_to_remove:
            self.timer_threads.remove(thread)

    def kill_timer(self):
        self.stop_timer()
        for timer_thread in self.timer_threads:
            timer_thread.join()
