import pysweep

class Timer:
    def __init__(self, master, callback, period, resolution):
        # calls callback whenever the time changes more than period seconds (which will be every second by default), checking for this condition every resolution seconds (0.01 by default)
        self.master = master
        self.callback = callback
        self.period = int(period * 1000)
        self.resolution = int(resolution * 1000)
        self.start_time = 0
        self.previous_tick_time = 0
        self.next_tick_time = 0
        self.stop_time = 0
        self.timing_mode = False
        self.poll_freq = max(self.resolution, 1) # poll at the requested resolution, converting to milliseconds.

    def start_timer(self):
        self.start_time = pysweep.time()
        self.previous_tick_time = self.start_time
        self.next_tick_time = self.start_time # Used to have + self.period, but have it send two callbacks now so pysweeper can ceil the timer nicely :)
        self.callback(0, 0)

        if self.timing_mode == False:
            self.timing_mode = True
            self.poll_timer()
        # self.master.after(self.poll_freq, self.poll_timer)

    def poll_timer(self):
        if self.timing_mode == True:
            curtime = pysweep.time()
            elapsed = curtime - self.start_time
            sincelasttick = curtime - self.previous_tick_time
            if curtime > self.next_tick_time:
                self.previous_tick_time = curtime
                self.next_tick_time += self.period
                self.callback(elapsed, sincelasttick)

            self.master.after(self.poll_freq, self.poll_timer)

    def stop_timer(self):
        if not self.timing_mode:
            return # Do nothing if already stopped
        self.stop_time = pysweep.time()
        self.timing_mode = False

        curtime = pysweep.time()
        elapsed = curtime - self.start_time
        sincelasttick = curtime - self.previous_tick_time
        self.previous_tick_time = curtime
        self.next_tick_time = 0
        self.stop_time = curtime

        self.callback(elapsed, sincelasttick)

    def kill_timer(self):
        self.stop_timer()
        # We don't really need to clean up in this version

