#!/usr/bin/python
# coding:utf-8

import os.path

SETTINGS = dict(template_path=os.path.join(os.path.dirname(__file__),"templates"),
				static_path=os.path.join(os.path.dirname(__file__), "static"),
				debug=True
				)

DB_HOST     = 'localhost'
DB_PORT     = 27017
DB_PASSWORD = None

WX_PLAT_TOKEN = 'infixz'

TAX_START_CONST = 3500

TAX_CONST = {
	1:(0.03,0),
	2:(0.1,105),
	3:(0.2,555),
        4:(0.25,1005),
	5:(0.3,2755),
	6:(0.35,5505),
	7:(0.45,13505)
}


tmp = "<xml>\
<ToUserName><![CDATA[{{toUser}}]]></ToUserName>\
<FromUserName><![CDATA[{{fromUser}}]]></FromUserName>\
<CreateTime>{{int_time}}</CreateTime>\
<MsgType><![CDATA[text]]></MsgType>\
<Content><![CDATA[{{Content}}]]></Content>\
</xml>"
