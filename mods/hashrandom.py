import hashlib

class HashRandomFactory:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep

        self.rngs = []

    def get_rng(self):
        rng = HashRandom()
        self.rngs.append(rng)
        return rng

def powoftwo(n):
    i = 1
    while i < n:
        i *= 2
    return i

class HashRandom:
    def __init__(self):
        self.source = ''
        self.hasher = hashlib.sha512()

    def update(self, updatestring):
        self.source += updatestring
        self.hasher.update(updatestring.encode('utf-8'))

    def get_source(self):
        return self.source

    def random(self, numerator, denominator, updatestring="CATS"):
        # numerator = number of mines
        # denominator = number of undetermined squares
        # returns 1 with probability of a mine

        i = 0
        dividend = powoftwo(denominator)
        while True:
            update = "{} {}\n".format(updatestring, str(i))
            self.source += update
            self.hasher.update(update.encode('utf-8'))

            digest = self.hasher.hexdigest()
            number = int(digest, 16)
            
            remainder = number % dividend
            if remainder >= denominator:
                i += 1
                continue

            return remainder < numerator

mods = {"HashRandom": HashRandomFactory}
