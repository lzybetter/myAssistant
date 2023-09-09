import yaml
import os


class Config:
    __BASE_PATH = os.getcwd()
    __CONFIG_PATH = os.path.join(__BASE_PATH, 'config')
    __CONFIG_NAME = 'test.yaml'
    __SCHEDULER_DB_FILE_NAME = 'scheduler.db'
    __LOG_FILE_NAME = 'myAssistant.log'
    __CONFIG_DICT = {}

    def __init__(self):
        if self.__CONFIG_DICT == {}:
            with open(os.path.join(self.__CONFIG_PATH, self.__CONFIG_NAME)) as f:
                self.__CONFIG_DICT = yaml.safe_load(f)

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):
            Config._instance = object.__new__(cls)
        return Config._instance

    @property
    def CONFIG_PATH(self):
        return self.__CONFIG_PATH

    @property
    def BASE_PATH(self):
        return self.__BASE_PATH

    def get_scheduler_db_file_path(self):
        try:
            return os.path.join(self.__CONFIG_PATH, self.__CONFIG_DICT['SCHEDULER_DB_PATH'],
                                self.__SCHEDULER_DB_FILE_NAME)
        except:
            return os.path.join(self.__CONFIG_PATH, 'schedule_db', self.__SCHEDULER_DB_FILE_NAME)

    def set_scheduler_db_path(self, new_path):
        self.__CONFIG_DICT['SCHEDULER_DB_PATH'] = new_path
        with open(os.path.join(self.__CONFIG_PATH, self.__CONFIG_NAME), 'w') as f:
            f.write(yaml.safe_dump(self.__CONFIG_DICT, sort_keys=False))

    def get_log_file_path(self):
        try:
            return os.path.join(self.__CONFIG_PATH, self.__CONFIG_DICT['LOG_PATH'], self.__LOG_FILE_NAME)
        except:
            return os.path.join(self.__CONFIG_PATH, 'log', self.__LOG_FILE_NAME)

    def set_log_path(self, new_path):
        self.__CONFIG_DICT['LOG_PATH'] = new_path
        with open(os.path.join(self.__CONFIG_PATH, self.__CONFIG_NAME), 'w') as f:
            f.write(yaml.safe_dump(self.__CONFIG_DICT, sort_keys=False))

    def get_proxy(self):
        try:
            return self.__CONFIG_DICT['PROXY']
        except:
            return None

    def set_proxy(self, new_proxy):
        self.__CONFIG_DICT['PROXY'] = new_proxy
        with open(os.path.join(self.__CONFIG_PATH, self.__CONFIG_NAME), 'w') as f:
            f.write(yaml.safe_dump(self.__CONFIG_DICT, sort_keys=False))
