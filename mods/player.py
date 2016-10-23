import tkinter

# Little decorator for ensuring the event is a certain value
# wasn't sure where it should go, of if you wouldn't like it!
# So i just shoved it here xD (see on_enabled, on_disabled)

def allow_events(event_names):
    if not isinstance(event_names, (list, tuple)):
        event_names = (event_names,)
    def _allow_events(f):
        def wrapper(s, hn, e):
            if e in event_names:
                return f(s, hn, e)
            else:
                return
        return wrapper
    return _allow_events

        

game_mode_name = "Video Player"
class Player:
    hooks = {}
    required_events = []
    required_protocls = []
    
    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "AllModsLoaded"): [self.mods_loaded],
            ("gamemode", "EnableGameMode"): [self.on_enable],
            ("gamemode", "DisableGameMode"): [self.on_disable],
        }

    def mods_loaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

    @allow_events(game_mode_name)
    def on_enable(self, hn, e):
        print("enabled!")

    @allow_events(game_mode_name)
    def on_disable(self, hn, e):
        print("disabled!")
        
        
mods = {"Player": Player}
