# -*- coding: utf-8 -*-
from __future__ import division
import time
import hashlib
import functools

import tornado.template as template

import requests
from lxml import etree

from local_setting import WX_PLAT_TOKEN, TAX_CONST, TAX_START_CONST, tmp


class Retry(object):
    """This class will create a retry decorator.
    Using is_valid to judge if wrapped function failed.
    Retry if wrapped function failed.
    Retry at most MAX_TRIES times.
    """
    MAX_TRIES = 3

    def __init__(self, is_valid=id, max_tries=3):
        self.is_valid = is_valid
        self.MAX_TRIES = max_tries

    def __call__(self, func):
        @functools.wraps(func)
        def retried_func(*args, **kwargs):
            resp = None
            tries = 0
            while tries < self.MAX_TRIES:
                try:
                    resp = func(*args, **kwargs)
                except Exception:
                    continue
                if self.is_valid(resp):
                    break
                tries += 1
            return resp
        return retried_func


retry = Retry()


def parse(xml_string):
    """
    parse xml string, return a message object if succeed, else return None
    :param xml_string: xml string that we-chat post to server
    :return: None or a message object
    """
    # TODO
    # add support for other type of message
    # add support for encrypted message
    xml = etree.fromstring(xml_string)
    developer = xml.find('ToUserName').text
    sender = xml.find('FromUserName').text
    create_time = xml.find('CreateTime').text
    message_type = xml.find('MsgType').text
    message = None

    # 信息类型是text
    if message_type == 'text':
        message_id = xml.find('MsgId').text
        content = xml.find('Content').text
        Loader = template.Loader("templates")
        text_resp = Loader.load("text_reply.xml")
        if content.startswith('!menu'):
            temp = tuple(content[3:].split(u'，'))
            param1 = int(temp[0])
            param2 = int(temp[1])
            RespContent = """
# 中英互译：直接输入中文\n
# 查询税后收入：！薪水<数字金额>，<发多少个月工资>例如 “#12000,13”
""" % calc_tax(param1,param2)
            return t.generate(toUser=sender,
                            fromUser=developer,
                            int_time=int(time.time()),
                            Content=RespContent)
        if content.startswith(u'#'):
            temp = tuple(content[1:].split(u'，'))
            param1 = int(temp[0])
            param2 = int(temp[1])
            RespContent = """
* 月入：%s ，年入：%s *\n
月实际收入：%s\n税赋：%s\n
年实际奖金：%s\n税赋：%s\n
* 一年实际总收入：%s *
""" % calc_tax(param1,param2)
            return t.generate(toUser=sender,
                            fromUser=developer,
                            int_time=int(time.time()),
                            Content=RespContent)
        if type(content).__name__ == 'unicode':
            content = content.encode('utf-8')
        RespContent = youdao(content)
        return t.generate(toUser=sender,
                          fromUser=developer,
                          int_time=int(time.time()),
                          Content=RespContent)


    # 信息类型是event
    if message_type == "event":
        eventContent = xml.find("Event").text
        if eventContent == "subscribe":
            RespContent = """
感谢你的关注。
若有疑问请在微信中查找添加 infixz。
目前实用功能有：
1.中英文互译(感谢有道翻译)。
2.流言(这是一个匿名聊天板)。
3.薪水(帮你计算税后所得)。
输入 !menu 查看操作指令"""
            t = template.Template(tmp)
            return t.generate(toUser=sender,
                                fromUser=developer,
                                int_time=int(time.time()),
                                Content=RespContent)


def check_signature(signature, timestamp, nonce):
    """check if we-chat message is valid"""
    if not signature or not timestamp or not nonce or not WX_PLAT_TOKEN:
        return False
    tmp_lst = [WX_PLAT_TOKEN, timestamp, nonce]
    tmp_lst.sort()
    tmp_str = ''.join(tmp_lst)
    return hashlib.sha1(tmp_str).hexdigest() == signature


def calc_tax(salary_m,num):
    # 检查参数类型
    if not (type(salary_m) == int and type(num) == int):
        return False
    # init param
    salary_m_in_real = 0
    salary_m_tax = 0
    salary_y = 0            # 每年账面薪水（包含奖金）
    base = salary_m - TAX_START_CONST
    income = 0              # 每年实际入账（包含税后奖金）
    bonus = num             # 账面奖金
    bonus_in_real = 0
    bonus_tax = 0
    if 12 < num <= 30:
        bonus = salary_m * (num - 12)
    elif num == 12:
        bonus = 0
    salary_y = salary_m * 12 + bonus
    # 计算税率
    # part1:salary part
    (rate,deduct) = tax_rate(base)
    salary_m_tax = (salary_m - TAX_START_CONST) * rate - deduct
    salary_m_in_real = salary_m - salary_m_tax
    # part2:bonus part
    (rate,deduct) = tax_rate(bonus)
    bonus_tax = bonus * rate - deduct
    bonus_in_real = bonus - bonus_tax
    # part3:total
    income = salary_m_in_real * 12 + bonus_in_real
    return (salary_m,salary_y,
            salary_m_in_real,salary_m_tax,
            bonus_in_real,bonus_tax,
            income)


def tax_rate(money):
    if money == 0:
        return (0.0,0)
    if 0 < money <= 1500:
        return TAX_CONST[1]
    if 1500 < money <= 4500:
        return TAX_CONST[2]
    if 4500 < money <= 9000:
        return TAX_CONST[3]
    if 9000 < money <= 35000:
        return TAX_CONST[4]
    if 35000 < money <= 55000:
        return TAX_CONST[5]
    if 55000 < money <= 80000:
        return TAX_CONST[6]
    if 80000 < money:
        return TAX_CONST[7]
        

def youdao(word):
    url = r'http://fanyi.youdao.com/openapi.do?keyfrom=sorrible&key=1660616686&type=data&doctype=json&version=1.1&q='
    builded_url = url+word
    result = requests.get(builded_url).json()
    if result['errorCode'] == 0:
        if 'basic' in result.keys():
            trans = '%s:\n%s\n%s\n网络释义：\n%s'%(result['query'],''.join(result['translation']),' '.join(result['basic']['explains']),'\n'.join(result['web'][0]['value']))
            return trans
        else:
            trans = '%s:\n基本翻译:%s\n'%(result['query'],''.join(result['translation']))
    elif result['errorCode'] == 20:
        return '查询词过长'
    elif result['errorCode'] == 30:
        return '无法进行有效的翻译'
    elif result['errorCode'] == 40:
        return '不支持的语言类型'
    else:
        return '你输入的单词%s无法翻译,请检查拼写'% word
