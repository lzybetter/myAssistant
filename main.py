from util.PluginManager import PluginManager


if __name__ == "__main__":
    manager = PluginManager()

    # Load and execute plugins
    manager.load_plugins()
    plugin_names = manager.get_plugin_name_list()
    print(plugin_names)