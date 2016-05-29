#!/usr/bin/python
# coding:utf-8

import tornado.httpserver as httpserver
import tornado.ioloop as ioloop
import tornado.web as web

from pymongo import MongoClient

from config import WX_PLAT_TOKEN, SETTINGS, DB_HOST, DB_PORT
from util import check_signature,parse

class IndexHandler(web.RequestHandler):
	"""docstring for IndexHandler"""
	def get(self):
		# greetingwords = self.get_argument('greeting','hello')
		# self.write(greetingwords + u',再次见面分外眼红')
		self.render('index.html')

class ResumeHandler(web.RequestHandler):
	"""docstring for ResumeHandler"""
	def get(self):
		self.render('resume.html')


class LeavMsgHandler(web.RequestHandler):
	"""docstring for MsgHandler"""
	def post(self):
		print 'MsgHandler post'
		try:
			self.coll = self.application.db.leavemsg
		except:
			print 'except'

class GoogleVerifyHandler(web.RequestHandler):
	def get(self):
		self.render('google05df3613559d1aa7.html')

class WxHandler(web.RequestHandler):
	# TODO:
	# Add async post method
	"""handler for ddddd on weixin_platform"""
	def get(self):
		"""check token"""
		print 'check wx'
		if self._check_signature():
			self.write(self.get_query_argument('echostr'))
		else:
			self.write('Naughty boy~')
			
	def post(self):
		"""response weixin msg"""
		if not self._check_signature():
			self.write('Naughty boy~')
		resp = parse(self.request.body)
		print 'POSTed a msg'
		self.write(resp)
		
	def _check_signature(self):
		try:
			nonce = self.get_query_argument('nonce')
			signature = self.get_query_argument('signature')
			timestamp = self.get_query_argument('timestamp')
		except Exception as exception:
 			print 'Checked False'
			return False
		else:
			return check_signature(signature, timestamp, nonce)


class App(web.Application):
	"""docstring for App"""
	def __init__(self):
		handlers = [(r'/',IndexHandler),
					(r'/resume',ResumeHandler),
					(r'/leavemsg',LeavMsgHandler),
					(r'/weixin',WxHandler),
					(r'/google05df3613559d1aa7.html',GoogleVerifyHandler)
					]
		self.db = MongoClient(DB_HOST,DB_PORT)['usertest']
		web.Application.__init__(self,handlers,**SETTINGS)



if __name__ == '__main__':
	http_server = httpserver.HTTPServer(App())
	print 'App has being run on server'
	http_server.listen(8880)
	ioloop.IOLoop.instance().start()
