import base64
import hashlib
import hmac
import json
import ssl
import threading
import time
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket
import os
from util.config import Config


STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class TTS(object):

    def __init__(self, APP_ID, API_KEY, API_SECRET):

        self.APP_ID = APP_ID
        self.API_KEY = API_KEY
        self.API_SECRET = API_SECRET
        self.config = Config()

        # 公共参数(common)
        self.common_args = {"app_id": self.APP_ID}

        # 业务参数(business)
        self.business_args = {
            "aue": "lame", "sfl":1, "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"
        }

    # 生成业务数据流参数(data)
    @staticmethod
    def gen_data(text):
        data = {
            "status": 2,  # 数据状态，固定为2 注：由于流式合成的文本只能一次性传输，不支持多次分段传输，此处status必须为2。
            "text": str(base64.b64encode(text.encode('utf-8')), "UTF8")
        }
        return data

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.API_SECRET.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.API_KEY, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url

class TTSWebSocket(object):

    def __init__(self, msg, tts_obj):
        self.msg = msg
        self.tts = tts_obj
        self.url = tts_obj.create_url()
        self.data = []
        self.flag = False
        self.audio_dir = "audio/"
        self.ws_listener = None
        self.config = Config()
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.url, on_message=self.on_message,
                                         on_error=self.on_error, on_close=self.on_close)

    def on_message(self, ws, msg):
        try:
            message = json.loads(msg)
            print(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            status = message["data"]["status"]

            if code == 0:
                self.data.append(audio)
            else:
                err_msg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, err_msg, code))
            if status == 2:
                print("------>数据接受完毕")
                self.flag = True
                self.ws.close()
        except Exception as e:
            print("receive msg,but parse exception:", e)
            # print(sys.exc_info()[0])

    def on_error(self, ws, error):
        print("### error:", error)

    def on_close(self, ws,  *args):
        print("### closed ###")

    def on_open(self, ws):
        d = {"common": self.tts.common_args,
             "business": self.tts.business_args,
             "data": self.tts.gen_data(self.msg[1]),
             }
        d = json.dumps(d)
        print("------>开始发送文本数据: {}".format(self.msg))
        self.ws.send(d)

    def get_result(self):
        self.flag = False

        if self.data:
            audio_path = os.path.join(self.config.BASE_PATH, self.config.get_config("TTS")["AUDIO_PATH"])
            print(self.config.get_config("TTS"))
            audio_file = os.path.join(audio_path, "result.mp3")
            print(audio_path)
            with open(audio_file, 'wb') as f:
                for _r in self.data:
                    f.write(base64.b64decode(_r))
            return audio_file
        return "error：未收到任何信息"

    def run(self):
        self.ws.on_open = self.on_open
        self.ws_listener = threading.Thread(target=self.ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
        self.ws_listener.daemon = True
        self.ws_listener.start()

        timeout = 15
        end_time = time.time() + timeout
        while True:
            if time.time() > end_time:
                raise websocket.WebSocketTimeoutException
            if self.flag:
                result = self.get_result()
                return result

