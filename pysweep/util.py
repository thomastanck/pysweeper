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
