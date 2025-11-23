import os
import importlib

class PluginManager:
    def __init__(self, root):
        self.root = root
        self.plugins = []

    def load_plugins(self):
        plugin_dir = os.path.join(self.root, "plugins")
        for file in os.listdir(plugin_dir):
            if file.startswith("plugin_") and file.endswith(".py"):
                module = importlib.import_module(f"plugins.{file[:-3]}")
                if hasattr(module, "register"):
                    self.plugins.append(module.register())

    def before_reply(self, text):
        for p in self.plugins:
            if hasattr(p, "before_reply"):
                text = p.before_reply(text)
        return text

    def after_reply(self, text):
        for p in self.plugins:
            if hasattr(p, "after_reply"):
                text = p.after_reply(text)
        return text

