# Little decorator for ensuring the gamemode is enabled
def gamemode(game_mode_name):
    def _allow_events(f):
        def wrapper(self, *args, **kwargs):
            if self.gamemodeselector.is_enabled(game_mode_name):
                return f(self, *args, **kwargs)
            else:
                return
        return wrapper
    return _allow_events

def own_game_mode(f):
    def wrapper(self, *args, **kwargs):
        if self.gamemodeselector.is_enabled(self.game_mode_name):
            return f(self, *args, **kwargs)
        else:
            return
    return wrapper


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

    def __init__(self, widget, event=None, time=0, x=0, y=0, x_root=0, y_root=0, lmb=False, rmb=False, inbounds=False):
        self.widget = widget
        self.event = event # "LD", "LU", "M", etc.
        self.time = time
        self.x = x
        self.y = y
        self.x_root = x_root
        self.y_root = y_root
        self.lmb = lmb
        self.rmb = rmb
        self.inbounds = inbounds
        self.__isfrozen = True



class BoardClick:
    # Stripped down version of the tkinter event, and adds some restrictions so it'll be easier to debug in the future
    # One motivation for the attribute restrictions is that we frequently compute row/col out of x/y.
    # In order to prevent mixing up events which are supposed to have x/y and events which are supposed to have row/col,
    # we'll simply force BoardClick to use row/col only.
    __isfrozen = False
    tile_size = (16, 16)
    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError( "%r is a frozen class, cannot set %s" % (self, key))
        object.__setattr__(self, key, value)

    def __init__(self, event=None, time=0, row=0, col=0, lmb=False, rmb=False):
        self.event = event
        self.time = time
        self.row = row
        self.col = col
        self.lmb = lmb
        self.rmb = rmb
        self.__isfrozen = True

    def fromClickerEvent(self, e):
        self.event = e.event # "LD", "LU", "M", etc.
        self.time = e.time
        self.row = e.y//self.tile_size[1]
        self.col = e.x//self.tile_size[0]
        self.lmb = e.lmb
        self.rmb = e.rmb
