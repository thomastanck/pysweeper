import tkinter

class Menu:
    hooks = {}
    required_events = []
    required_protocols = []
    master = None
    menubar = None
    menus = {}

    def init_menu(master):
        Menu.master = master

        Menu.menubar = tkinter.Menu(Menu.master)
        Menu.master.config(menu=Menu.menubar)

    def add_menu(label, menu):
        Menu.menubar.add_cascade(label=label, menu=menu)

    def remove_menu(label, menu):
        Menu.menubar.delete(label)

