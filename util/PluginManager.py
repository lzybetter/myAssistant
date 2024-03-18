import importlib.util
import os

from util.base_plugin import BasePlugin


class PluginManager:
    PLUGIN_DIR = "custom_plugins"

    def __init__(self):
        self.plugins = {}
        self.plugin_dir = PluginManager.PLUGIN_DIR

    def load_plugins(self):
        for root, dirs, files in os.walk(self.plugin_dir):
            for file in files:
                if file.endswith(".py"):
                    plugin_name = os.path.splitext(file)[0]
                    plugin_path = os.path.join(root, file)
                    print(plugin_name)
                    self.load_plugin(plugin_name, plugin_path)

    def load_plugin(self, plugin_name, plugin_path):
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for member_name in dir(module):
            member = getattr(module, member_name)

            if callable(member) and hasattr(member, "__bases__") and BasePlugin in member.__bases__:
                print(member)
                self.plugins[plugin_name] = member()
                print(f"Plugin '{plugin_name}' loaded successfully.")

    def execute_plugins(self, *args, **kwargs):
        for plugin_name, plugin_instance in self.plugins.items():
            print(f"Executing plugin '{plugin_name}':")
            plugin_instance.run_plugin(self.callback, *args, **kwargs)

    def execute_plugin(self, plugin_name, *args, **kwargs):
        if plugin_name in self.plugins:
            print(f"Executing plugin '{plugin_name}':")
            self.plugins[plugin_name].run_plugin(self.callback, *args, **kwargs)
        else:
            print(f"Plugin '{plugin_name}' not found.")

    def get_plugin_name_list(self):

        return [plugin[0] for plugin in self.plugins.items()]

    def callback(self, result):
        print(f"Plugin '{result['plugin_name']}' returned:")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Result: {result['result']}")
        else:
            print(f"Error: {result['error']}")