from util.config import Config
from util.PluginManager import PluginManager
from flask import Flask

if __name__ == "__main__":

    ## 初始化
    ## flask初始化
    app = Flask(__name__)
    ## 配比初始化
    config = Config()
    ## 插件管理器
    manager = PluginManager(config)

    # Load and execute plugins
    manager.load_plugins()

    manager.start_scheduler()
    print("初始化完成")
    app.run()
