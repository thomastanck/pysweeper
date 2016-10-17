import os

import imp
import inspect

import tkinter

class PySweep3:
    def __init__(self, master):
        self.master = master
        self.hook_prefix = "pysweep3"
        self.bind_events = []
        self.bind_protocols = []
        self.load_pysweep3_mods()

    def bind_tkinter_event(self, event_name):
        if event_name not in self.bind_events:
            hook = self.hook_prefix + event_name
            self.master.bind(event_name, lambda e,hook=hook: self.handle_event(hook, e))
            self.bind_events.append(event_name)

    def bind_tkinter_protocol(self, protocol_name):
        if protocol_name not in self.bind_protocols:
            hook = self.hook_prefix + protocol_name
            self.master.protocol(protocol_name, lambda e=None,hook=hook: self.handle_event(hook, e))
            self.bind_protocols.append(protocol_name)

    def load_pysweep3_mods(self):
        # Mods dictionary
        # Key is the module name (directory name if package, filename without .py extension if file)
        # Value is a tuple containing the path to the module and either imp.PY_SOURCE or imp.PKG_DIRECTORY
        self.mods_list = {}

        # Dict of mods we've loaded (name: moduleinstance)
        self.mods = {}

        # A dictionary with hook strings as keys and a list of callbacks as values
        self.hooks = {}

        # load mods here
        alreadyfound = self.find_mods('mods')
        print("Files found: {}".format(alreadyfound))
        print("Mods found: {}".format(self.mods_list))

        for name, mod in self.mods_list.items():
            module, _ = self.import_mod(name, mod[0], mod[1])
            if hasattr(module, name):
                moduleclass = getattr(module, name)
                print("Attempting to load mod {}".format(name))
                moduleinstance = self.load_mod(moduleclass, name)
                if moduleinstance != None:
                    print("Loaded mod {}".format(name))
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

    def load_mod(self, moduleclass, name):
        if inspect.isclass(moduleclass):
            moduleinstance = moduleclass(self.master, self)
            if (hasattr(moduleinstance, "hooks") and isinstance(moduleclass.hooks, dict)):
                self.mods[name] = moduleinstance
                self.register_hooks(moduleinstance)
                return moduleinstance
        return None

    def register_hooks(self, moduleinstance):
        # First check if it requires any event or protocol bindings.
        if hasattr(moduleinstance, "required_events"):
            for event_name in moduleinstance.required_events:
                self.bind_tkinter_event(event_name)
        if hasattr(moduleinstance, "required_protocols"):
            for protocol_name in moduleinstance.required_protocols:
                self.bind_tkinter_protocol(protocol_name)

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
                        self.mods_list[modname] = (mod, imp.PKG_DIRECTORY)
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
