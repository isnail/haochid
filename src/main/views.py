__author__ = 'biyanbing'
import datetime

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login as system_login

from plat.models import Plat
from lib.sina.weibo import APIClient as sina
from lib.tencent.weibo import APIClient as tencent
from user.models import User
from utils import *
import settings

default_password = 'SDf32sdf'


def callback(req, plat):
    if plat not in ('s', 't'):
        raise Http404
    code = req.GET.get('code')
    if plat == 's':
        plat = Plat.objects.get(name=plat)
        client = sina(plat.app_key, plat.app_secret)
        r = client.request_access_token(code, 'http://haochid.com/callback/s')
        access_token, expires_in, uid = r.access_token, r.expires_in, r.uid
        client.set_access_token(access_token, expires_in)
        u = client.users.show.get(uid=uid)
        try:
            user = User.objects.get(uid=uid)
        except User.DoesNotExist:
            user = User.objects.create_user(uid, default_password)
        user.nick_name = u.screen_name
        user.avatar = u.avatar_large or u.profile_image_url
        user.gender = u.gender
        user.location = u.location
        user.ip = get_ip(req)
        user.access_token = access_token
        user.expires_in = datetime.datetime.now() + datetime.timedelta(seconds=int(expires_in))
        user.save()
        user = authenticate(username=uid, password=default_password)
        system_login(req, user)
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        open_id = req.GET.get('openid')
        open_key = req.GET.get('openkey')
        plat = Plat.objects.get(name=plat)
        client = tencent(plat.app_key, plat.app_secret)
        r = client.request_access_token(code, 'http://haochid.com/callback/t')
        access_token, expires_in = r.access_token, r.expires_in
        client.set_access_token(access_token, expires_in, open_id, get_ip(req))

        u = client.user.info.get()
        print u
        return HttpResponse(u)

