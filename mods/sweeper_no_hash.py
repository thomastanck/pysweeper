from mods.pysweeper import PySweeper
import random

class PythonRand:
    def random(self, numerator, denominator):
        return random.randint(0, denominator-1) < numerator

    def update(self, *args, **kwargs):
        pass # lol

class NoHashRandom(PySweeper):
    game_mode_name = "NoHashRandom"
    rng_class = PythonRand
    is_default_mode = False

mods = {"NoHashRandom": NoHashRandom}
