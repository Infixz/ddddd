"""
httpserver & manager
"""
# coding:utf-8

import tornado.ioloop as ioloop
import tornado.options
from tornado.options import define, options
define("port", default=8084, help='server will running on the given port', type=int)

from apps import App


if __name__ == '__main__':
    tornado.options.parse_command_line()
    App().listen(options.port)
    print 'Start listenning' + str(options.port)
    ioloop.IOLoop.current().start()
