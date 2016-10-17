import tkinter

class Menu:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep3):
        self.master = master
        self.pysweep3 = pysweep3

        self.menubar = tkinter.Menu(self.master)
        self.master.config(menu=self.menubar)

        self.menus = []

    def add_menu(self, label, menu):
        self.menus.append((label, menu))
        self.menubar.add_cascade(label=label, menu=menu)

