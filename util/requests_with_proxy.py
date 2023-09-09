import requests
import os
from util import config
import json

class RequestWithProxy:

    __proxies = {}
    __no_proxy = []
    def __init__(self):
        c = config.Config()
        proxies_tmp = c.get_proxy()
        if proxies_tmp:
            for k in sorted(proxies_tmp):
                if k in ('http', 'https'):
                    if 'http://' in proxies_tmp[k] or "https://" in proxies_tmp[k]:
                        self.__proxies[k] = proxies_tmp[k]
                    else:
                        self.__proxies[k] = "http://" + proxies_tmp[k]
                elif k == 'proxy_web':
                    for w in proxies_tmp[k]:
                        if ('http' in self.__proxies and self.__proxies['http']) or ('https' in self.__proxies and self.__proxies['https']):
                            if 'http://' in w:
                                self.__proxies[w] = self.__proxies['http']
                            elif 'https://' in w:
                                self.__proxies[w] = self.__proxies['https']
                            else:
                                self.__proxies["https://" + w] = self.__proxies['https']
                elif k == 'no_proxy_web':
                    for w in proxies_tmp[k]:
                        self.__no_proxy.append(w.replace("https://", "").replace("http://", ""))
            if self.__no_proxy:
                os.environ['NO_PROXY'] = ','.join(self.__no_proxy)

    def get(self, url, headers=None):
        try:
            if url.replace("https://", "").replace("http://", "") in self.__no_proxy:
                r = requests.get(url=url, headers=headers)
            else:
                r = requests.get(url=url, headers=headers, proxies=self.__proxies)
            return r
        except:
            return None

    def post(self, url, data=None, json_d=None, headers=None):
        pass