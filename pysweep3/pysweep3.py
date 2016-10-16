import os

import imp
import inspect

import tkinter

class PySweep3:
    def __init__(self, master):
        self.master = master
        self.load_mods()

    def load_mods(self):
        # Mods dictionary
        # Key is the module name (directory name if package, filename without .py extension if file)
        # Value is a tuple containing the path to the module and either imp.PY_SOURCE or imp.PKG_DIRECTORY
        self.mods_list = {}

        # Dict of mods we've loaded (name: moduleinstance)
        self.mods = {}

        # A dictionary with hook strings as keys and a list of callbacks as values
        self.hooks = {}

        pysweep3hooklist = [
            ("<ButtonPress-1>", "pysweep3<ButtonPress-1>"),
            ("<B1-Motion>", "pysweep3<B1-Motion>"),
            ("<ButtonRelease-1>", "pysweep3<ButtonRelease-1>"),
            ("<Motion>", "pysweep3<Motion>"),
            ("<Enter>", "pysweep3<Enter>"),
            ("<Leave>", "pysweep3<Leave>"),
            ("<KeyPress>", "pysweep3<KeyPress>"),
            ("<KeyRelease>", "pysweep3<KeyRelease>"),
        ]
        for hook in pysweep3hooklist:
            self.master.bind(hook[0], lambda e,hook=hook[1]: self.handle_event(hook, e))

        # load mods here
        alreadyfound = self.get_mods('mods')
        print("Files found: {}".format(alreadyfound))
        print("Mods found: {}".format(self.mods_list))

        for name, mod in self.mods_list.items():
            module, _ = self.import_mod(name, mod[0], mod[1])
            if hasattr(module, name):
                moduleclass = getattr(module, name)
                print("Attempting to load mod {}".format(name))
                moduleinstance = self.get_moduleinstance(moduleclass)
                if moduleinstance != None:
                    print("Loaded mod {}".format(name))
                    self.mods[name] = moduleinstance
                    self.register_hooks(moduleinstance)
                else:
                    print("{} is an invalid mod".format(name))
        print("Mods loaded: {}".format(list(self.mods.keys())))

        self.handle_event("AllModsLoaded", None)

    def is_mod(self, path):
        if os.path.isdir(path):
            return self.is_package_mod(path)
        elif os.path.isfile(path):
            return self.is_file_mod(path)

    def is_package_mod(self, path):
        return os.path.isfile(os.path.join(path, '__init__.py'))

    def is_file_mod(self, path):
        return path.endswith('.py') and not os.path.basename(path).startswith('_')

    def ignore_dir(self, path):
        return (os.path.basename(path).startswith("_") or os.path.basename(path).startswith("."))

    def ignore_file(self, path):
        return os.path.basename(path).startswith(".")

    def get_moduleinstance(self, moduleclass):
        if inspect.isclass(moduleclass):
            moduleinstance = moduleclass(self.master, self)
            if (hasattr(moduleinstance, "hooks") and isinstance(moduleclass.hooks, dict)):
                return moduleinstance
        return None


    def register_hooks(self, moduleinstance):
        for hook in moduleinstance.hooks:
            if hook in self.hooks:
                self.hooks[hook].extend(moduleinstance.hooks[hook])
            else:
                self.hooks[hook] = moduleinstance.hooks[hook]

    def get_mods(self, path, alreadyfound=[]):
        # Finds mods in path recursively
        # alreadyfound keeps track of every file and directory we've accessed
        for mod in os.listdir(path):
            mod = os.path.join(path, mod)

            if os.path.isdir(mod) and not self.ignore_dir(mod):
                # DIRECTORY
                for found in alreadyfound:
                    if os.path.samefile(mod, found):
                        print("Already found: {}".format(mod))
                        break
                else:
                    # this mod is not yet found
                    print("Found: {}".format(mod))
                    alreadyfound.append(mod)
                    if self.is_package_mod(mod):
                        modname = os.path.basename(mod)
                        self.mods_list[modname] = (mod, imp.PKG_DIRECTORY)
                    else:
                        # Was not a package mod, recurse to find more mods inside
                        alreadyfound = self.get_mods(mod, alreadyfound)

            elif os.path.isfile(mod) and not self.ignore_file(mod):
                # FILE
                for found in alreadyfound:
                    if os.path.samefile(mod, found):
                        print("Already found: {}".format(mod))
                        break
                else:
                    # this mod is not yet found
                    print("Found: {}".format(mod))
                    alreadyfound.append(mod)
                    if self.is_file_mod(mod):
                        modname = os.path.basename(mod)[:-3]
                        self.mods_list[modname] = (mod, imp.PY_SOURCE)
        return alreadyfound

    def import_mod(self, name, path, type_):
        if type_ == imp.PY_SOURCE:
            with open(path) as mod:
                module = imp.load_module(name, mod, path, ('.py', 'U', type_))
        elif type_ == imp.PKG_DIRECTORY:
            module = imp.load_module(name, None, path, ('', '', type_))
        else:
            raise TypeError('Unsupported module type')
        return module, os.path.getmtime(path)

    def handle_event(self, hookname, event):
        if hookname in self.hooks:
            for callab in self.hooks[hookname]:
                callab(event)
