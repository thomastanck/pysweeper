import tkinter
import tkinter.filedialog

from pysweep.util import gamemode
from pysweep import Timer
import pysweep

display_events = {
    "TILENUMBER": num,
    "TILEOTHER" : oth,
    "COUNTER"   : coun,
    "FACE"      : fac,
    "TIMER"     : tim,
}

def num(gamedisplay, n, r, c):
    gamedisplay.set_tile_number(r, c, n)

def oth(gamedisplay, t, r, c):
    gamedisplay.set_tile_other(r, c, t)

def coun(gamedisplay, n):
    gamedisplay.set_mine_counter(n)

def fac(gamedisplay, t):
    gamedisplay.set_face(t)

def tim(gamedisplay, n):
    gamedisplay.set_timer(n)

game_mode_name = "Video Player"

class Player:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "AllModsLoaded"): [self.mods_loaded],
            ("gamemode", "EnableGameMode"): [self.on_enable],
            ("gamemode", "DisableGameMode"): [self.on_disable],
        }

        self.gamedisplay = self.pysweep.gamedisplay

        self.timer = Timer(self.master, self.tick, period=0.001, resolution=0.001)
        self.vid = None
        self.vid_start = 0

    def mods_loaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.vidmod = self.pysweep.mods["VideoFile"]
        self.gamemodeselector.register_game_mode(game_mode_name)

    def tick(self, elapsed, sincelasttick):
        if self.vid:
            if self.vid_start == 0:
                # find vidstart
                for event in self.vid:
                     if event[0] in display_events:
                         self.vidstart = event[1]
                         break
            end = self.vid_start + elapsed
            start = end - sincelasttick
            for event in self.vid:
                if event[0] in display_events and start <= event[1] < end:
                    args = event[2:]
                    display_events[event[0]](self.gamedisplay, *args)

    @gamemode(game_mode_name)
    def on_enable(self, hn, e):
        print("enabled!")
        self.window = tkinter.Toplevel(self.master)
        self.rewindbutton = tkinter.Button(self.window, text="Bekku", command=self.rewind)
        self.playbutton = tkinter.Button(self.window, text="Purei", command=self.play)
        self.forwardbutton = tkinter.Button(self.window, text="Foowaado", command=self.forward)
        self.loadbutton = tkinter.Button(self.window, text="Roodo", command=self.load)
        # step forward backward, other images and stuff, etc
        # You'll probably want Frames and Canvases in here.
        self.rewindbutton.pack()
        self.playbutton.pack()
        self.forwardbutton.pack()
        self.loadbutton.pack()

    @gamemode(game_mode_name)
    def on_disable(self, hn, e):
        print("disabled!")
        self.window.destroy()
        del self.window

    def rewind(self):
        print("rewind pressed")
        self.timer.stop_timer()
        self.timer = Timer(self.master, self.tick, period=0.001, resolution=0.001)
        self.tick(0,0)
    def play(self):
        print("play pressed")
        self.timer.start_timer()
    def forward(self):
        print("forward pressed")
        self.timer.stop()
        self.timer = Timer(self.master, self.tick, period=0.001, resolution=0.001)
        self.tick(sys.maxsize,sys.maxsize)
    def load(self):
        print("load pressed")
        filename = tkinter.filedialog.askopenfilename()
        print("filename: {}".format(filename))
        f = open(filename, 'rb')
        contents = f.read()
        print("contents:")
        print(contents)
        self.vid = self.vidmod.new_video_file(self.pysweep.gamedisplay, "","")
        try:
            self.vid.vidbytes = contents
        except:
            try:
                self.vid.vidstr = contents.decode('utf-8')
            except:
                raise ValueError('Failed to read video file')
        print('Video file:')
        print(self.vid.vid)


mods = {"Player": Player}
