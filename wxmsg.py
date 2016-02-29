# -*- coding: utf-8 -*-
import time
from uuid import uuid4
from pkg_resources import resource_string

import ujson as json
from tornado import gen
from tornado.websocket import websocket_connect
from redis import StrictRedis
from jinja2 import Template

from config import DB_SERVER, DB_HOST, DB_PASSWORD, DB_PORT, demo_url
from q_protocol import enc, dec


DEMO_SHOWROOM = 0
DEMO_GUEST    = 1
DEMO_WEB      = 2


def build_response(type, target, **kwargs):
    # TODO
    # add support for news response
    """
    根据提供的参数生成回复，默认是json格式，如果需要xml格式则需加上两个关键字参数：
    format='xml', source='wx openid'。
    不同的回复类型需要不同的关键字参数，详情参见:http://bit.ly/1CWj1Vw
    目前支持以下几种回复类型：text | image | voice | video | music
    """
    format = kwargs.pop('format', 'json')
    if type == 'text':
        if 'content' not in kwargs:
            raise Exception('too few arguments!')
    elif type == 'image' or type == 'voice' or type == 'video':
        if 'media_id' not in kwargs:
            raise Exception('too few arguments!')
    elif type == 'music':
        if 'thumb_media_id' not in kwargs:
            raise Exception('too fee arguments!')
    if format == 'json':
        response = {'touser': target, 'msgtype': type}
        response[type] = {k: v for k, v in kwargs.items()}
        response = json.dumps(response, ensure_ascii=False)
    else:
        template = resource_string(__name__, 'response.template')
        response = Template(template).render(info=kwargs, type=type,
                                             target=target,
                                             create_time=str(int(time.time())))
    return response


class WxMsg(object):
    def __init__(self, source, target, create_time, msg_id = None):
        self.source = source
        self.target = target
        self.crate_time = create_time
        self.msg_id = msg_id

    @gen.coroutine
    def response(self):
        raise gen.Return('')


class Subscribe(WxMsg):
    def __init__(self, source, target, create_time):
        super(Subscribe, self).__init__(source, target, create_time)


class Unsubscribe(WxMsg):
    def __init__(self, source, target, create_time):
        super(Unsubscribe, self).__init__(source, target, create_time)


class ScanSubscribe(WxMsg):
    def __init__(self, source, target, create_time, event_key, ticket):
        super(ScanSubscribe, self).__init__(source, target, create_time)
        self.event_key = event_key
        self.ticket = ticket


class Scan(WxMsg):
    def __init__(self, source, target, create_time, event_key, ticket):
        super(Scan, self).__init__(source, target, create_time)
        self.event_key = event_key
        self.ticket = ticket

    @gen.coroutine
    def response(self):
        db = StrictRedis(DB_HOST, port=DB_PORT, password=DB_PASSWORD)
        host_id = db.hget('LIMIT_QR', self.ticket)
        #print 'LIMIT_QR {}, {}'.format(self.event_key, host_id)
        oid = str(uuid4())
        ws_conn = yield websocket_connect(DB_SERVER)
        msg = enc('DB_TEMP_AUTHCODE', {'ID': self.source,
                                           'OID': oid,
                                           'HID': host_id,
                                           'TYPE': DEMO_SHOWROOM})
        ws_conn.write_message(msg)
        resp = yield ws_conn.read_message()
        event, args = dec(resp)
        if event == 'DB_OK' and args['OID'] == oid:
            auth_code = args['AUTHCODE']
            raise gen.Return(build_response('text', source=self.target,
                                            target=self.source, format='xml',
                                            content=demo_url.format(auth_code)))
        else:
            raise gen.Return('')


class Click(WxMsg):
    def __init__(self, source, target, create_time, event_key):
        super(Click, self).__init__(source, target, create_time)
        self.event_key = event_key


class View(WxMsg):
    def __init__(self, source, target, create_time, event_key):
        super(View, self).__init__(source, target, create_time)
        self.event_key = event_key


class ScanPush(WxMsg):
    def __init__(self, source, target, create_time, event_key,
                 scan_code_info, scan_type, scan_result):
        super(ScanPush, self).__init__(source, target, create_time)
        self.event_key = event_key
        self.scan_code_info = scan_code_info
        self.scan_type = scan_type
        self.scan_result = scan_result


class ScanWait(WxMsg):
    def __init__(self, source, target, create_time, event_key,
                 scan_code_info, scan_type, scan_result):
        super(ScanWait, self).__init__(source, target, create_time)
        self.event_key = event_key
        self.scan_code_info = scan_code_info
        self.scan_type = scan_type
        self.scan_result = scan_result


class TextMsg(WxMsg):
    def __init__(self, source, target, create_time, msg_id, content):
        super(TextMsg, self).__init__(source, target, create_time, msg_id)
        self.content = content

