import asyncio
import importlib.util
import os
import threading
from datetime import datetime

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
                schedule = self.__get_schedule_time(name)
                self.loop.create_task(self.execute_plugin_async(name, schedule))

            self.loop.run_forever()

        thread = threading.Thread(target=scheduler)
        thread.daemon = True
        thread.start()


    async def execute_plugin_async(self, plugin_name, schedule, *args, **kwargs):

        while True:
            if plugin_name in self.plugins:
                print(f"Executing plugin '{plugin_name}':")
                if schedule['mode'] == "INTERVAL" or schedule['mode'] == "CONTIENUOUS":
                    result = self.execute_plugin(plugin_name, *args, **kwargs)
                    token = self.config.get_config('TELEGRAM')['BOT_TOKEN']
                    chat_id = self.config.get_config('TELEGRAM')['CHAT_ID']
                    await self.send_message_async(token, chat_id, result)
                elif schedule['mode'] == "FIX":
                    now = datetime.now()
                    if now.hour == schedule['HOUR'] and now.minute == schedule['MINUTE']:
                        result = self.execute_plugin(plugin_name, *args, **kwargs)
                        token = self.config.get_config('TELEGRAM')['BOT_TOKEN']
                        chat_id = self.config.get_config('TELEGRAM')['CHAT_ID']
                        await self.send_message_async(token, chat_id, result)
            else:
                print(f"Plugin '{plugin_name}' not found.")

            print(schedule)
            await asyncio.sleep(schedule['INTERVAL_TIME'])


    async def send_message_async(self, bot_token, chat_id, text):
        proxy = telegram.request.HTTPXRequest(proxy_url='http://127.0.0.1:8889')
        bot = telegram.Bot(token=bot_token, request=proxy)
        await bot.send_message(chat_id=chat_id, text=text)

    def __get_schedule_time(self, plugin_name):
        schedule = {}
        try:
            schedule_config = self.config.get_plugin_config('SCHEDULE', self.plugins_path[plugin_name])
            mode = schedule_config['MODE'].upper()
            print(mode)
            schedule['mode'] = mode
            if mode == 'INTERVAL':
                if 'INTERVAL_TIME' in schedule_config.keys():
                    interval_time = (schedule_config['INTERVAL_TIME']['HOUR'] * 3600 +
                                     schedule_config['INTERVAL_TIME']['MINUTE'] * 60 +
                                        schedule_config['INTERVAL_TIME']['SECOND'])
                    if interval_time < 30:
                        schedule['INTERVAL_TIME'] = 30
                    else:
                        schedule['INTERVAL_TIME'] = interval_time
                else:
                    schedule['INTERVAL_TIME'] = 30
            elif mode == 'FIX' and "RUN_TIME" in schedule_config.keys():
                schedule['HOUR'] = schedule_config["RUN_TIME"]['HOUR']
                schedule['MINUTE'] = schedule_config["RUN_TIME"]['MINUTE']
                schedule['INTERVAL_TIME'] = 30
            elif mode == 'CONTIENUOUS':
                schedule['INTERVAL_TIME'] = 30
            else:
                schedule['mode'] = 'CONTIENUOUS'
                schedule['INTERVAL_TIME'] = 30
        except:
            schedule['mode'] = 'CONTIENUOUS'
            schedule['INTERVAL_TIME'] = 30

        return schedule