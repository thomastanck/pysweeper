import hashlib

class HashRandomFactory:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3

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
        self.entropy = ''
        self.hasher = hashlib.sha512()

    def update(self, updatestring):
        self.entropy += updatestring
        self.hasher.update(updatestring.encode('utf-8'))

    def get_entropy(self):
        return self.entropy

    def random(self, numerator, denominator, updatestring="CATS"):
        # numerator = number of mines
        # denominator = number of undetermined squares
        # returns 1 with probability of a mine

        i = 0
        while True:
            update = "{} {}".format(updatestring, str(i))
            self.entropy += update
            self.hasher.update(update.encode('utf-8'))

            digest = self.hasher.hexdigest()
            number = int(digest, 16)

            dividend = powoftwo(denominator)
            remainder = number % dividend
            if remainder >= denominator:
                continue
            elif remainder < numerator:
                return True
            else:
                return False

mods = {"HashRandom": HashRandomFactory}
