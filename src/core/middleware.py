import time

from django.contrib.auth import logout
from django.shortcuts import redirect

from lib.sina.weibo import APIClient as sina
from lib.tencent.weibo import APIClient as tencent

from utils import *
from user.models import User

class PlatMiddleware(object):
    def process_request(self, request):
        # user = request.user
        # if user and isinstance(user, User) and user.plat and user.plat.name in ('s', 't'):
        #     if user.plat.name == 's':
        #         client = sina(user.plat.app_key, user.plat.app_secret)
        #         client.set_access_token(user.access_token, user.expires_in)
        #     else:
        #         client = tencent(user.plat.app_key, user.plat.app_secret)
        #         client.set_access_token(user.access_token, user.expires_in, user.openid, get_ip(request))
        #     if client.is_expires():
        #         logout(request)
        #     else:
        #         pass
        #         r = client.refresh_token(user.access_token)
        #         user.access_token = r.access_token
        #         user.expires_in = r.expires_in
        #         user.save()
        return None
