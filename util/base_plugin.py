class BasePlugin:
    def __init__(self, plugin_name, title):
        self.plugin_name = plugin_name
        self.title = title

    def run_plugin(self):
        raise NotImplementedError("Subclasses must implement run_plugin method")
