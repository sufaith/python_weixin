#coding:utf-8
from server.page_handler import PageHandler
from server.wx_handler import WxHandler
from server.wxauthorize import WxSignatureHandler

'''web解析规则'''

urlpatterns = [
    (r'/wxsignature', WxSignatureHandler),  # 微信签名
    (r'/page/(.*)', PageHandler),  # 加载页面
    (r'/wx/(.*)', WxHandler),  # 网页授权
    ]
