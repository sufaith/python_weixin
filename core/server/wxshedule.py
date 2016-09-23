from core.logger_helper import logger
import tornado.ioloop
import requests
import json
from core.server.wxconfig import WxConfig
from core.cache.tokencache import TokenCache


class WxShedule(object):
    """
    定时任务调度器

    excute                      执行定时器任务
    get_access_token            获取微信全局唯一票据access_token
    get_jsapi_ticket           获取JS_SDK权限签名的jsapi_ticket
    """
    _token_cache = TokenCache()  # 微信token缓存实例
    _expire_time_access_token = 7000 * 1000  # token过期时间

    def excute(self):
        """执行定时器任务"""
        logger.info('【获取微信全局唯一票据access_token】>>>执行定时器任务')
        tornado.ioloop.IOLoop.instance().call_later(0, self.get_access_token)
        tornado.ioloop.PeriodicCallback(self.get_access_token, self._expire_time_access_token).start()
        # tornado.ioloop.IOLoop.current().start()

    def get_access_token(self):
        """获取微信全局唯一票据access_token"""
        url = WxConfig.config_get_access_token_url
        r = requests.get(url)
        logger.info('【获取微信全局唯一票据access_token】Response[' + str(r.status_code) + ']')
        if r.status_code == 200:
            res = r.text
            logger.info('【获取微信全局唯一票据access_token】>>>' + res)
            d = json.loads(res)
            if 'access_token' in d.keys():
                access_token = d['access_token']
                # 添加至redis中
                self._token_cache.set_access_cache(self._token_cache.KEY_ACCESS_TOKEN, access_token)
                # 获取JS_SDK权限签名的jsapi_ticket
                self.get_jsapi_ticket()
                return access_token
            elif 'errcode' in d.keys():
                errcode = d['errcode']
                logger.info(
                    '【获取微信全局唯一票据access_token-SDK】errcode[' + errcode + '] , will retry get_access_token() method after 10s')
                tornado.ioloop.IOLoop.instance().call_later(10, self.get_access_token)
        else:
            logger.error('【获取微信全局唯一票据access_token】request access_token error, will retry get_access_token() method after 10s')
            tornado.ioloop.IOLoop.instance().call_later(10, self.get_access_token)

    def get_jsapi_ticket(self):
        """获取JS_SDK权限签名的jsapi_ticket"""
        access_token = self._token_cache.get_cache(self._token_cache.KEY_ACCESS_TOKEN)
        if access_token:
            url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % access_token
            r = requests.get(url)
            logger.info('【微信JS-SDK】获取JS_SDK权限签名的jsapi_ticket的Response[' + str(r.status_code) + ']')
            if r.status_code == 200:
                res = r.text
                logger.info('【微信JS-SDK】获取JS_SDK权限签名的jsapi_ticket>>>>' + res)
                d = json.loads(res)
                errcode = d['errcode']
                if errcode == 0:
                    jsapi_ticket = d['ticket']
                    # 添加至redis中
                    self._token_cache.set_access_cache(self._token_cache.KEY_JSAPI_TICKET, jsapi_ticket)
                else:
                    logger.info('【微信JS-SDK】获取JS_SDK权限签名的jsapi_ticket>>>>errcode[' + errcode + ']')
                    logger.info('【微信JS-SDK】request jsapi_ticket error, will retry get_jsapi_ticket() method after 10s')
                    tornado.ioloop.IOLoop.instance().call_later(10, self.get_jsapi_ticket)
            else:
                logger.info('【微信JS-SDK】request jsapi_ticket error, will retry get_jsapi_ticket() method after 10s')
                tornado.ioloop.IOLoop.instance().call_later(10, self.get_jsapi_ticket)
        else:
            logger.error('【微信JS-SDK】获取JS_SDK权限签名的jsapi_ticket时,access_token获取失败, will retry get_access_token() method after 10s')
            tornado.ioloop.IOLoop.instance().call_later(10, self.get_access_token)

if __name__ == '__main__':

    wx_shedule = WxShedule()
    """执行定时器"""
    wx_shedule.excute()


