import tornado.web


class PageHandler(tornado.web.RequestHandler):
    """
    微信handler处理类
    """

    def post(self, flag):

        if flag == 'index':
            '''首页'''
            self.render('index.html')
