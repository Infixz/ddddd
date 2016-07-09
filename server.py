"""
Server listening deter port
"""
# coding:utf-8

import tornado.ioloop as ioloop
import tornado.options
from tornado.options import define, options
define("port", default=8085, help='run on given port', type=int)

from apps import App


if __name__ == '__main__':
    tornado.options.parse_command_line()
    App().listen(options.port)
    ioloop.IOLoop.current().start()
