# Little decorator for ensuring the gamemode is enabled
def gamemode(game_mode_name):
    def _allow_events(f):
        def wrapper(self, hn, e):
            if self.gamemodeselector.is_enabled(game_mode_name):
                return f(self, hn, e)
            else:
                return
        return wrapper
    return _allow_events
