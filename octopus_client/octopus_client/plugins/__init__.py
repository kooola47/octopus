import importlib
import os
import sys

PLUGIN_DIR = os.path.dirname(__file__)

def load_plugins():
    plugins = {}
    for fname in os.listdir(PLUGIN_DIR):
        if fname.endswith('.py') and fname != '__init__.py':
            mod_name = f"octopus_client.plugins.{fname[:-3]}"
            if mod_name in sys.modules:
                mod = importlib.reload(sys.modules[mod_name])
            else:
                mod = importlib.import_module(mod_name)
            plugins[fname[:-3]] = mod
    return plugins
