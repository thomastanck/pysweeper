import threading, time

class Timer:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3

        # This mod is pretty benign and doesn't do much except give other mods TimerObj's
        self.timers = [] # A list of timers it has made

    def get_timer(self, callback, resolution=1):
        timerobj = TimerObj(self.master, callback, resolution)
        self.timers.append(timerobj)
        return timerobj

class TimerObj:
    def __init__(self, master, callback, resolution):
        # calls callback whenever the time changes more than resolution (which will be every second by default)
        self.master = master
        self.callback = callback
        self.resolution = resolution
        self.start_time = 0
        self.current_time = 0
        self.stop_time = 0
        self.timing_mode = False
        self.poll_freq = max(int(resolution/100*1000), 1) # poll 100 times faster than the requested resolution, then convert to milliseconds. not sure if we should do this.

    def start_timer(self):
        self.start_time = time.time()
        self.current_time = self.start_time
        self.timing_mode = True

        self.callback(0, 0)

        self.poll_timer()
        # self.master.after(self.poll_freq, self.poll_timer)

    def poll_timer(self):
        if self.timing_mode == True:
            curtime = time.time()
            elapsed = curtime - self.start_time
            sincelasttick = curtime - self.current_time
            if sincelasttick > self.resolution:
                self.current_time = curtime
                self.callback(elapsed, sincelasttick)

            self.master.after(self.poll_freq, self.poll_timer)

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

    def kill_timer(self):
        self.stop_timer()
        # We don't really need to clean up in this version

mods = {"Timer": Timer}
