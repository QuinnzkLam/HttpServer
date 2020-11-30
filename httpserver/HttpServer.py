"""
    主程序代码
"""

from socket import *
from config import *
from threading import Thread
import re
import json


# 和后端应用程序去做交互  webframe
def connect_frame(env):
    # 是单独用于和webframe做交互的
    s = socket()
    try:
        # 此时httpserver变成了客户端，因此，要给webframe（服务器）发送内容
        s.connect((frame_ip, frame_port))
    except Exception as e:
        print(e)
        return
        # 要将字典类型数据发送给webframe
    data = json.dumps(env)
    s.send(data.encode())
    # 当发送完之后，我们要等待后端应用 处理反馈结果
    try:
        data = s.recv(1024 * 1024 * 10).decode()
        return json.loads(data)
    except:
        return


# 封装成类
class HTTPServer:
    def __init__(self):
        # 将config文件中的配置，做一个引用
        self.host = HOST
        self.port = PORT
        self.create_socket()
        self.bind()

    # 创建套接字
    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, DEBUG)

    def bind(self):
        self.sockfd.bind((self.host, self.port))
        self.address = (self.host, self.port)

    def server_forever(self):
        self.sockfd.listen(3)
        print('Listen the port %d' % self.port)
        while True:
            connfd, addr = self.sockfd.accept()
            print('Connect from', addr)
            # 当客户端连接过来，我们就要采用多线程进行处理
            # 也就意味着，一旦有客户端连接过来，我们就要做好接收http请求的准备了
            t = Thread(target=self.handle, args=(connfd,))
            t.setDaemon(True)  # 主程序退出,子线程也退出
            t.start()

    # handle具体处理客户端的请求
    def handle(self, connfd):
        request = connfd.recv(4096).decode()
        # print(request)
        # httpserver -->webframe  包括两方面 内容：请求方法 请求内容 {'method': 'GET', 'info': '/'}
        # webframe -->httpserver  包括两方面 内容：响应码/具体响应内容{'status': '200','data': 'xxxx'}
        # 从请求中提取出请求类型和请求内容
        pattarn = r'(?P<method>[A-Z]+)\s(?P<info>/\S*)'
        try:
            env = re.match(pattarn, request).groupdict()
            # re.match得到的是一个match对象，想要取到值，还得用group，
            # 只不过，这里用的是groupdict
            # groupdict 匹配出来的结果是一个字典类型，方便我们查看 {组名：结果}...
        except:
            connfd.close()
            return
        else:
            # print(env)
            data = connect_frame(env)
            if data:
                # 如果有数据，组织相应
                self.response(connfd, data)

    def response(self, connfd, data):
        if data['status'] == '200':
            responseHeader = 'HTTP/1.1 200 OK\r\n'
            responseHeader += 'Content-Type:text/html\r\n'
            responseHeader += '\r\n'
            responseBody = data['data']
        elif data['status'] == '404':
            responseHeader = 'HTTP/1.1 404 Not Found\r\n'
            responseHeader += 'Content-Type:text/html\r\n'
            responseHeader += '\r\n'
            responseBody = data['data']
        # 将内容发送给浏览器
        response_data = responseHeader + responseBody
        connfd.send(response_data.encode())


if __name__ == '__main__':
    httpd = HTTPServer()
    httpd.server_forever()  # 启动服务
