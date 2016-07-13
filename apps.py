"""
Controler & Enterance
"""
# coding: utf-8

import tornado.web as web
from local_setting import SETTINGS
from handlers import WxpIntroHandler, WxHandler

class App(web.Application):
    """
    wechatp app
    include a intro page and wxmsg handler
    """
    def __init__(self):
        handlers = [
            (r'/', WxpIntroHandler),
            (r'/wx_i', WxHandler),
            ]
        web.Application.__init__(self, handlers, **SETTINGS)
