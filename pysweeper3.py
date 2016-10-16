import os, platform
import tkinter
from pysweep3 import PySweep3

def pushwindowtotop():
    if platform.system() == 'Darwin':  # How Mac OS X is identified by Python
        os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')

def main():
    root = tkinter.Tk()
    root.title('PySweeper3')
    root.grab_set()
    app = PySweep3(root)
    pushwindowtotop()
    root.mainloop()
    try:
        root.destroy()
    except tkinter.TclError as e:
        pass

if __name__ == '__main__':
    main()