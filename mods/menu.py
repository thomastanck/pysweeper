import tkinter

class Menu:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep

        self.menubar = tkinter.Menu(self.master)
        self.master.config(menu=self.menubar)

    def add_menu(self, label, menu):
        self.menubar.add_cascade(label=label, menu=menu)

    def remove_menu(self, label, menu):
        self.menubar.delete(label)

mods = {"Menu": Menu}
