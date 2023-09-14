
class BasePlugin:

    def __init__(self):
        self.__plugin_name = ""


    def get_result(self):
        """
        用以返回插件的结果，所有插件都必须通过该方法返回结果
        返回结果的类型必须是指定的类型
        :return:
        """
        raise NotImplemented


class FinanceValue:

    def __init__(self):
        self.__name = ""
        self.__value = ""

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_value(self, value):
        self.__value = value

    def get_value(self):
        return self.__value