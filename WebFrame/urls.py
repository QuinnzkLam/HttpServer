"""
    数据处理路由
"""
from views import *

urls = [
    ("/hello", hello),
    ("/time", get_time),
    ("/bye", bye)
]