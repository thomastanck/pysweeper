# Hack to push window to top
from os import system
from platform import system as platform

def pushwindowtotop():
    if platform() == 'Darwin':  # How Mac OS X is identified by Python
        system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

import tkinter
from PIL import Image, ImageTk
import time

class PySweeper:
    def __init__(self, master):
        self.master = master
        self.mainapp = Demo1(self.master)

class Demo1:
    def __init__(self, master):
        self.master = master
        self.frame = tkinter.Frame(self.master)
        self.button1 = tkinter.Button(self.frame, text = 'New Window', width = 25, command = self.new_window)
        self.button1.pack()
        self.frame.pack()
    def new_window(self):
        self.newWindow = tkinter.Toplevel(self.master)
        self.app = Demo2(self.newWindow)

class Demo2:
    def __init__(self, master):
        self.master = master
        self.frame = tkinter.Frame(self.master)
        self.quitButton = tkinter.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.frame.pack()
    def close_windows(self):
        self.master.destroy()

def main():
    root = tkinter.Tk()
    root.title('PySweeper')
    app = PySweeper(root)
    pushwindowtotop()
    root.mainloop()
    try:
        root.destroy()
    except tkinter.TclError as e:
        pass

if __name__ == '__main__':
    main()