

class WxConfig(object):
    """
    微信开发--基础配置

    """
    AppID = 'wxxxxxxxxxxxxxxxx'  # AppID(应用ID)
    AppSecret = '024a7fcxxxxxxxxxxxxxxxxxxxx'  # AppSecret(应用密钥)

    """微信网页开发域名"""
    AppHost = 'http://xxxxxx.com'

    '''获取access_token'''
    config_get_access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (AppID, AppSecret)

    '''自定义菜单创建接口'''
    menu_create_url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token='

    '''自定义菜单查询接口'''
    menu_get_url = 'https://api.weixin.qq.com/cgi-bin/menu/get?access_token='

    '''自定义菜单删除接口'''
    menu_delete_url = 'https://api.weixin.qq.com/cgi-bin/menu/delete?access_token='

    '''微信公众号菜单映射数据'''
    """重定向后会带上state参数，开发者可以填写a-zA-Z0-9的参数值，最多128字节"""
    wx_menu_state_map = {
        'menuIndex0': '%s/page/index' % AppHost,  # 测试菜单1
    }

