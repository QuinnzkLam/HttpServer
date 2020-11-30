"""
    模拟后端应用
"""

from socket import *
import json
from settings import *
from threading import Thread
from urls import *


# 处理请求
class Application(Thread):
    def __init__(self, connfd):
        super().__init__()
        self.connfd = connfd

    # 执行线程功能
    def run(self):
        # 接收请求{'method':'GET','info':'xxxx'}
        request = self.connfd.recv(1024).decode()
        request = json.loads(request)  # 转换为字典
        if request['method'] == 'GET':
            # 如果是GET请求类型，就考虑下info是啥内容
            if request['info'] == '/' or request['info'][-5:] == '.html':
                response = self.get_html(request['info'])
            else:
                response = self.get_data(request['info'])
        elif request['method'] == 'PORT':
            pass
        # 将数据发送给httpserver
        response = json.dumps(response)
        self.connfd.send(response.encode())
        self.connfd.close()

    def get_html(self, info):
        if info == '/':
            filename = STATIC + '/index.html'
        else:
            filename = STATIC + info

        try:
            fd = open(filename)
        except Exception as e:
            with open(STATIC + '/404.html') as f:
                return {'status': '404', 'data': f.read()}
        else:
            return {'status': '200', 'data': fd.read()}

    # 处理非网页情况
    def get_data(self, info):
        for url, func in urls:
            if url == 'info':
                return {'status': '200', 'data': func()}
        return {'status': '404', 'data': "Sorry..."}


def main():
    s = socket()
    # DEBUG 这种是不是支持调试，由用户自己决定
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, DEBUG)
    s.bind((frame_ip, frame_port))
    s.listen(3)
    print('Listen the port 8800')
    while True:
        c, addr = s.accept()
        print('Connect from', addr)

        # 一旦有客户端连接过来，创建线程类
        app = Application(c)
        app.setDaemon(True)
        app.start()

if __name__ == '__main__':
    main()