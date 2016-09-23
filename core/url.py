from core.server.wxauthorize import WxSignatureHandler
from core.server.page_handler import PageHandler
from core.server.wx_handler import WxHandler


'''web解析规则'''

urlpatterns = [
    (r'/wxsignature', WxSignatureHandler),  # 微信签名
    (r'/page/(.*)', PageHandler),  # 加载页面
    (r'/wx/(.*)', WxHandler),  # 网页授权
    ]
