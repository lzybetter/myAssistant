from util.global_config import GlobalConfig

http_proxy_config = GlobalConfig()
http_proxy_config.set_globalconfig("http_proxy", '127.0.0.1:8889')

print(http_proxy_config.get_globalconfig("http_proxy"))
print(http_proxy_config.get_globalconfig("https_proxy"))
