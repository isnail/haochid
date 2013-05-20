__author__ = 'biyanbing'

import urllib2, urllib


class Api(object):
    def __init__(self, app_key, app_secret, redirect_url, wtype, auth_url, api_url):
        self.app_key = app_key
        self.app_secret = app_secret
        self.wtype = wtype
        self.auth_url = auth_url
        self.api_url = api_url

    def get_access_token(self, code):
        data = {'client_id': self.app_key, 'client_secret': self.app_secret, 'grant_type': 'authorization_code',
                'code': code}



sina = Api('key', 'secret', 'redirect_url', 's', 'https://api.weibo.com/oauth2/', 'https://api.weibo.com/2/')
tencent = Api('key', 'secret', 'redirect_url', 't', 'https://open.t.qq.com/cgi-bin/oauth2/authorize', 'api_url')