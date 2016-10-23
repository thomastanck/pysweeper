import os

import imp
import inspect

import tkinter

from pysweep import Menu, GameDisplay, VideoFile

class PySweep:
    def __init__(self, master):
        self.master = master
        self.bind_events = []
        self.bind_protocols = []
        self.widget_bindname = "pysweep"
        self.bindable_widgets = {"pysweep": {"bindevent": self.bind_tkinter_event, "bindprotocol": self.bind_tkinter_protocol}}

        # Init our own stuff: Menu and GameDisplay
        self.gamedisplay = GameDisplay(master, self)
        Menu.init_menu(master)

        self.load_pysweep_mods()

    # this is a bindable_widgets so it must implement these two functions.
    # The "name" of the bindable widget is also the prefix to the event_name used for the hook.
    # In this case, it's "pysweep".
    def bind_tkinter_event(self, event_name):
        if event_name not in self.bind_events:
            hook = (self.widget_bindname, event_name)
            self.master.bind(event_name, lambda e,hook=hook: self.handle_event(hook, e))
            self.bind_events.append(event_name)

    def bind_tkinter_protocol(self, protocol_name):
        if protocol_name not in self.bind_protocols:
            hook = (self.widget_bindname, protocol_name)
            self.master.protocol(protocol_name, lambda e=None,hook=hook: self.handle_event(hook, e))
            self.bind_protocols.append(protocol_name)

    def load_pysweep_mods(self):
        # Mods dictionary
        # Key is the package name (directory name if package, filename without .py extension if file)
        # Value is a tuple containing the path to the module and either imp.PY_SOURCE or imp.PKG_DIRECTORY
        self.mods_path_dict = {}

        # Mod classes dict
        # Key is mod name, value is the mod's class
        self.mod_classes = {}

        # Dict of mods we've loaded (name: moduleinstance)
        self.mods = {}

        # A dictionary with hook strings as keys and a list of callbacks as values
        self.hooks = {}

        # load mods here
        alreadyfound = self.find_mods('mods')
        print("Files found: {}".format(alreadyfound))
        print("Mods found: {}".format(self.mods_path_dict))

        # Paths -> Classes
        for package_name, mod in self.mods_path_dict.items():
            module, _ = self.import_mod(package_name, mod[0], mod[1])
            if hasattr(module, "mods"):
                for modname, modclass in module.mods.items():
                    self.mod_classes[modname] = modclass
            else:
                print("Could not find mods in {}".format(package_name))

        # Classes -> Instances
        for name, modclass in self.mod_classes.items():
            print("Attempting to load mod {}".format(name))
            moduleinstance = self.load_mod(modclass, name)
            if moduleinstance != None:
                print("Loaded mod {}".format(name))
            else:
                print("{} is an invalid mod".format(name))

        print("Mods loaded: {}".format(list(self.mods.keys())))
        print("Registering bindings")
        for name, mod in self.mods.items():
            self.register_bindings(mod)

        self.handle_event(("pysweep", "AllModsLoaded"), None)

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

    def load_mod(self, moduleclass, name):
        if inspect.isclass(moduleclass):
            moduleinstance = moduleclass(self.master, self)
            if (hasattr(moduleinstance, "hooks") and isinstance(moduleclass.hooks, dict)):
                self.mods[name] = moduleinstance
                self.register_hooks(moduleinstance)
                return moduleinstance
        return None

    def register_bindings(self, moduleinstance):
        if hasattr(moduleinstance, "required_events"):
            for widget_name, event_name in moduleinstance.required_events:
                self.bindable_widgets[widget_name]["bindevent"](event_name)
        if hasattr(moduleinstance, "required_protocols"):
            for widget_name, protocol_name in moduleinstance.required_protocols:
                self.bindable_widgets[widget_name]["bindprotocol"](protocol_name)

    def register_hooks(self, moduleinstance):
        # Check if they have any widgets they want to allow other mods to bind to.
        if hasattr(moduleinstance, "bindable_widgets"):
            for name, widget in moduleinstance.bindable_widgets.items():
                self.bindable_widgets[name] = widget

        # Then register their callbacks into our hooks dict
        for hook in moduleinstance.hooks:
            if hook in self.hooks:
                self.hooks[hook].extend(moduleinstance.hooks[hook])
            else:
                self.hooks[hook] = moduleinstance.hooks[hook]

    def find_mods(self, path, alreadyfound=[]):
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
                        self.mods_path_dict[modname] = (mod, imp.PKG_DIRECTORY)
                    else:
                        # Was not a package mod, recurse to find more mods inside
                        alreadyfound = self.find_mods(mod, alreadyfound)

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
                        self.mods_path_dict[modname] = (mod, imp.PY_SOURCE)
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
                callab(hookname, event)
