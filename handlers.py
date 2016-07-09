"""
View
"""
import tornado.web as web
import tornado.gen as gen
from util import check_signature, parse


class WxpIntroHandler(web.RequestHandler):
    """
    wechatp intro page provider
    """
    def get(self):
        self.render('index.html')

    def post(self):
        pass


class WxHandler(web.RequestHandler):
    """
    handler for ddddd on weixin_platform
    """
    def get(self):
        """check token, only run once"""
        if self._check_signature():
            self.write(self.get_query_argument('echostr'))
        else:
            self.write('Naughty boy~')

    @gen.coroutine
    def post(self):
        if not self._check_signature():
            self.write('Naughty boy~')
        resp = yield parse(self.request.body)
        self.write(resp)

    def _check_signature(self):
        try:
            nonce = self.get_query_argument('nonce')
            signature = self.get_query_argument('signature')
            timestamp = self.get_query_argument('timestamp')
        except Exception as exception:
            return False
        else:
            return check_signature(signature, timestamp, nonce)
