import hashlib

class BoardGeneratorFactory:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3

        self.boardgenerators = []

    def get_boardgenerator(self, width, height, num_mines):
        boardgen = BoardGenerator(width, height, num_mines)
        self.boardgenerators.append(boardgen)
        return boardgen


class BoardGenerator:
    def __init__(self, width, height, num_mines):
        self.width, self.height = width, height
        self.num_mines = num_mines

        self.area = width*height
        self.generated = [0]*self.area
        self.numremaining = self.area
        self.minesremaining = num_mines

        self.entropy = ''
        self.hasher = hashlib.sha512()

    def index(row, col):
        return self.width*row + col

    def inbounds(row, col):
        return (0 <= row and row < self.height and
                0 <= col and col < self.width)

    def generate(self, row, col):
        index = self.index(row, col)
        if self.generated[index] == 1:
            return None # already generated! wyd

        update = "GEN {} {}\n".format(row, col)
        self.entropy.append(update)
        self.hasher.update(update.encode('utf-8'))

        digest = self.hasher.hexdigest()
        number = int(digest, 16)

        ismine = (number % self.numremaining < self.num_mines)

        self.generated[index] = 1
        self.numremaining -= 1
        if ismine:
            self.minesremaining -= 1

        return ismine

    def ungenerate(self, row, col):
        index = self.index(row, col)
        if self.generated[index] == 0:
            return # not yet generated! wyd

        update = "UNGEN {} {}\n".format(row, col)
        self.entropy.append(update)
        self.hasher.update(update.encode('utf-8'))

mods = {"BoardGenerator", BoardGeneratorFactory}
