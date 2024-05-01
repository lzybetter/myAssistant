import asyncio
import importlib.util
import os
import threading

from util.base_plugin import BasePlugin

import telegram

class PluginManager:
    PLUGIN_DIR = "custom_plugins"

    def __init__(self, config):
        self.plugins = {}
        self.plugin_dir = PluginManager.PLUGIN_DIR
        self.running_tasks = []
        # 插件所在目录
        self.plugins_path = {}
        # self.loop = asyncio.new_event_loop()
        self.config = config

    def load_plugins(self):
        for root, dirs, files in os.walk(self.plugin_dir):
            for file in files:
                if file.endswith(".py"):
                    plugin_name = os.path.splitext(file)[0]
                    plugin_path = os.path.join(root, file)
                    self.load_plugin(plugin_name, plugin_path, root)

    def load_plugin(self, plugin_name, plugin_path, root):
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for member_name in dir(module):
            member = getattr(module, member_name)

            if callable(member) and hasattr(member, "__bases__") and BasePlugin in member.__bases__:
                print(member)
                self.plugins[plugin_name] = member()
                self.plugins_path[plugin_name] = root
                print(f"Plugin '{plugin_name}' loaded successfully.")

    def execute_plugins(self, *args, **kwargs):
        for plugin_name, plugin_instance in self.plugins.items():
            print(f"Executing plugin '{plugin_name}':")
            plugin_instance.run_plugin(self.callback, *args, **kwargs)

    def execute_plugin(self, plugin_name, *args, **kwargs):
        if plugin_name in self.plugins:
            print(f"Executing plugin '{plugin_name}':")
            return self.plugins[plugin_name].run_plugin(self.callback, *args, **kwargs)

        else:
            print(f"Plugin '{plugin_name}' not found.")
            return f"Plugin '{plugin_name}' not found."

    def get_plugin_name_list(self):

        return [plugin[0] for plugin in self.plugins.items()]

    def callback(self, result):

        print(f"Plugin '{result['plugin_name']}' returned:")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Result: {result['result']}")
        else:
            print(f"Error: {result['error']}")

    def start_scheduler(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        def scheduler():
            asyncio.set_event_loop(self.loop)
            for name in self.get_plugin_name_list():
                try:
                    schedule_time = int(
                        self.config.get_plugin_config(config_name='SCHEDULER_TIME', config_path=self.plugins_path[name]))
                except:
                    schedule_time = 10 * 60  # 默认十分钟运行一次
                self.loop.create_task(self.execute_plugin_async(name, schedule_time))

            self.loop.run_forever()

        thread = threading.Thread(target=scheduler)
        thread.daemon = True
        thread.start()


    async def execute_plugin_async(self, plugin_name, interval, *args, **kwargs):

        while True:
            if plugin_name in self.plugins:
                print(f"Executing plugin '{plugin_name}':")
                result = self.execute_plugin(plugin_name, *args, **kwargs)
                token = self.config.get_config('TELEGRAM')['BOT_TOKEN']
                chat_id = self.config.get_config('TELEGRAM')['CHAT_ID']
                await self.send_message_async(token, chat_id, result)
            else:
                print(f"Plugin '{plugin_name}' not found.")
            print(interval)
            await asyncio.sleep(interval)

    async def send_message_async(self, bot_token, chat_id, text):
        proxy = telegram.request.HTTPXRequest(proxy_url='http://127.0.0.1:8889')
        bot = telegram.Bot(token=bot_token, request=proxy)
        await bot.send_message(chat_id=chat_id, text=text)
