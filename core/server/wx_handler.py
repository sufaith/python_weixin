import tornado.web
from core.logger_helper import logger
from core.server.wxauthorize import WxConfig
from core.server.wxauthorize import WxAuthorServer
from core.cache.tokencache import TokenCache


class WxHandler(tornado.web.RequestHandler):
    """
    微信handler处理类
    """

    '''微信配置文件'''
    wx_config = WxConfig()
    '''微信网页授权server'''
    wx_author_server = WxAuthorServer()
    '''redis服务'''
    wx_token_cache = TokenCache()

    def post(self, flag):

        if flag == 'wxauthor':
            '''微信网页授权'''
            code = self.get_argument('code')
            state = self.get_argument('state')
            # 获取重定向的url
            redirect_url = self.wx_config.wx_menu_state_map[state]
            logger.debug('【微信网页授权】将要重定向的地址为:redirct_url[' + redirect_url + ']')
            logger.debug('【微信网页授权】用户同意授权，获取code>>>>code[' + code + ']state[' + state + ']')
            if code:
                # 通过code换取网页授权access_token
                data = self.wx_author_server.get_auth_access_token(code)
                openid = data['openid']
                logger.debug('【微信网页授权】openid>>>>openid[' + openid + ']')
                if openid:
                    # 跳到自己的业务界面
                    self.redirect(redirect_url)
                else:
                    # 获取不到openid
                    logger.debug('获取不到openid')