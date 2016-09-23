import time
import random
import string
import hashlib
from core.server.wxconfig import WxConfig
from core.cache.tokencache import TokenCache
from core.logger_helper import logger


class WxSign:
    """\
    微信开发--获取JS-SDK权限签名

    __create_nonce_str              随机字符串
    __create_timestamp              时间戳
    sign                            生成JS-SDK使用权限签名
    """

    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(string.encode('utf-8')).hexdigest()
        logger.debug('【微信JS-SDK】获取JS-SDK权限签名>>>>dict[' + str(self.ret) + ']')
        return self.ret

if __name__ == '__main__':

    token_cache = TokenCache()

    jsapi_ticket = token_cache.get_cache(token_cache.KEY_JSAPI_TICKET)
    # 注意 URL 一定要动态获取，不能 hardcode
    url = '%s/page/index' % WxConfig.AppHost
    sign = WxSign(jsapi_ticket, url)
    print(sign.sign())
