from core.logger_helper import logger
import hashlib
import tornado.web
import time
import urllib
import requests
import json
from urllib import parse
from core.server.wxconfig import WxConfig
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class WxAuthorServer(object):
    """
    微信网页授权server

    get_code_url                            获取code的url
    get_auth_access_token                   通过code换取网页授权access_token
    refresh_token                           刷新access_token
    check_auth                              检验授权凭证（access_token）是否有效
    get_userinfo                            拉取用户信息
    """

    """授权后重定向的回调链接地址，请使用urlencode对链接进行处理"""
    REDIRECT_URI = '%s/wx/wxauthor' % WxConfig.AppHost

    """
    应用授权作用域
    snsapi_base （不弹出授权页面，直接跳转，只能获取用户openid）
    snsapi_userinfo （弹出授权页面，可通过openid拿到昵称、性别、所在地。并且，即使在未关注的情况下，只要用户授权，也能获取其信息）
    """
    SCOPE = 'snsapi_base'
    # SCOPE = 'snsapi_userinfo'

    """通过code换取网页授权access_token"""
    get_access_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token?'

    """拉取用户信息"""
    get_userinfo_url = 'https://api.weixin.qq.com/sns/userinfo?'


    def get_code_url(self, state):
        """获取code的url"""
        dict = {'redirect_uri': self.REDIRECT_URI}
        redirect_uri = urllib.parse.urlencode(dict)
        author_get_code_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&%s&response_type=code&scope=%s&state=%s#wechat_redirect' % (WxConfig.AppID, redirect_uri, self.SCOPE, state)
        logger.debug('【微信网页授权】获取网页授权的code的url>>>>' + author_get_code_url)
        return author_get_code_url

    def get_auth_access_token(self, code):
        """通过code换取网页授权access_token"""
        url = self.get_access_token_url + 'appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (WxConfig.AppID, WxConfig.AppSecret, code)
        r = requests.get(url)
        logger.debug('【微信网页授权】通过code换取网页授权access_token的Response[' + str(r.status_code) + ']')
        if r.status_code == 200:
            res = r.text
            logger.debug('【微信网页授权】通过code换取网页授权access_token>>>>' + res)
            json_res = json.loads(res)
            if 'access_token' in json_res.keys():
                return json_res
            elif 'errcode' in json_res.keys():
                errcode = json_res['errcode']

    def get_userinfo(self, access_token, openid):
        """拉取用户信息"""
        url = self.get_userinfo_url + 'access_token=%s&openid=%s&lang=zh_CN' % (access_token, openid)
        r = requests.get(url)
        logger.debug('【微信网页授权】拉取用户信息Response[' + str(r.status_code) + ']')
        if r.status_code == 200:
            res = r.text
            json_data = json.loads((res.encode('iso-8859-1')).decode('utf-8'))
            logger.debug('【微信网页授权】拉取用户信息>>>>' + str(json_data))


class WxSignatureHandler(tornado.web.RequestHandler):
    """
    微信服务器签名验证, 消息回复

    check_signature: 校验signature是否正确
    """

    def data_received(self, chunk):
        pass

    def get(self):
        try:
            signature = self.get_argument('signature')
            timestamp = self.get_argument('timestamp')
            nonce = self.get_argument('nonce')
            echostr = self.get_argument('echostr')
            logger.debug('微信sign校验,signature='+signature+',&timestamp='+timestamp+'&nonce='+nonce+'&echostr='+echostr)
            result = self.check_signature(signature, timestamp, nonce)
            if result:
                logger.debug('微信sign校验,返回echostr='+echostr)
                self.write(echostr)
            else:
                logger.error('微信sign校验,---校验失败')
        except Exception as e:
            logger.error('微信sign校验,---Exception' + str(e))

    def post(self):
        body = self.request.body
        logger.debug('微信消息回复中心】收到用户消息' + str(body.decode('utf-8')))
        data = ET.fromstring(body)
        ToUserName = data.find('ToUserName').text
        FromUserName = data.find('FromUserName').text
        MsgType = data.find('MsgType').text
        if MsgType == 'text' or MsgType == 'voice':
            '''文本消息 or 语音消息'''
            try:
                MsgId = data.find("MsgId").text
                if MsgType == 'text':
                    Content = data.find('Content').text  # 文本消息内容
                elif MsgType == 'voice':
                    Content = data.find('Recognition').text  # 语音识别结果，UTF8编码
                if Content == u'你好':
                    reply_content = '您好,请问有什么可以帮助您的吗?'
                else:
                    # 查找不到关键字,默认回复
                    reply_content = "客服小儿智商不够用啦~"
                if reply_content:
                    CreateTime = int(time.time())
                    out = self.reply_text(FromUserName, ToUserName, CreateTime, reply_content)
                    self.write(out)
            except:
                pass

        elif MsgType == 'event':
            '''接收事件推送'''
            try:
                Event = data.find('Event').text
                if Event == 'subscribe':
                    # 关注事件
                    CreateTime = int(time.time())
                    reply_content = self.sys_order_reply
                    out = self.reply_text(FromUserName, ToUserName, CreateTime, reply_content)
                    self.write(out)
            except:
                pass

    def reply_text(self, FromUserName, ToUserName, CreateTime, Content):
        """回复文本消息模板"""
        textTpl = """<xml> <ToUserName><![CDATA[%s]]></ToUserName> <FromUserName><![CDATA[%s]]></FromUserName> <CreateTime>%s</CreateTime> <MsgType><![CDATA[%s]]></MsgType> <Content><![CDATA[%s]]></Content></xml>"""
        out = textTpl % (FromUserName, ToUserName, CreateTime, 'text', Content)
        return out

    def check_signature(self, signature, timestamp, nonce):
        """校验token是否正确"""
        token = 'test12345'
        L = [timestamp, nonce, token]
        L.sort()
        s = L[0] + L[1] + L[2]
        sha1 = hashlib.sha1(s.encode('utf-8')).hexdigest()
        logger.debug('sha1=' + sha1 + '&signature=' + signature)
        return sha1 == signature



