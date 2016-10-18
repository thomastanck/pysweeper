import fractions
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
    order  = 0
    while i < n:
        order += 1
        i *= 2
    return order, i

class HashRandom:
    def __init__(self):
        self.source = ''
        self.hasher = hashlib.sha512()
        self.hash_copy = None
        self.updates_to_copy = 0
        self.current_digest = None
        self.bits_remaining = 0

    def update(self, updatestring):
        if not updatestring:
            return
        self.source += updatestring
        self.hasher.update(updatestring.encode('utf-8'))
        self.hash_copy = self.hasher.copy()
        self.bits_remaining = 0 # forces us to digest if we want rands
        self.updates_to_copy = 0
        

    def get_source(self):
        return self.source

    def random(self, numerator, denominator):
        # numerator = number of mines
        # denominator = number of undetermined squares
        # returns 1 with probability of a mine

        if denominator == 0:
            raise ZeroDivisionError("denominator most be positive")
        if numerator == 0: return False # Will never be true
        if numerator == denominator: return True # will always be true

        # We reduce the fraction numerator/denominator so that we
        # require as few bits as possible to get our random number.
        d = fractions.gcd(numerator, denominator)
        numerator = numerator//d
        denominator = denominator//d

        bits_required, mask = powoftwo(denominator)
        remainder = denominator
        while remainder >= denominator:
            if self.bits_remaining >= bits_required:
                remainder = self.current_digest % mask
                self.current_digest //= mask
                self.bits_remaining -= bits_required
            else:
                self.hash_copy.update(b'\x00')
                self.current_digest = int(self.hash_copy.hexdigest(), 16)
                self.bits_remaining = 8*self.hash_copy.digest_size
                self.updates_to_copy += 1
        return remainder < numerator


mods = {"HashRandom": HashRandomFactory}
