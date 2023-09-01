class GlobalConfig:
    def __init__(self):
        """ 初始化 """
        global global_dict
        global_dict = {}

    def set_globalconfig(self, name, value):
        """
        设置全局变量
        :param name: 全局变量名称
        :param value: 全局变量值
        """
        global_dict[name] = value

    def get_globalconfig(self, name, defaultvalue=None):
        """
        获取全局变量
        :param name: 全局变量名称
        :param defaultvalue: 默认值，在无设置值时返回
        :return: 返回请求的全局变量值
        """
        try:
            return global_dict[name]
        except:
            return defaultvalue
