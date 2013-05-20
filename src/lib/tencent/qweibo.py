#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' 
    file: qweibo.py
    author：darkbull(http://darkbull.net)
    date: 2011-10-22
    desc:
        QQ微博api的python封装.
        QQ微博在线api文档参考：http://open.t.qq.com/resource.php?i=1,0
        说明：
        . 所有的api封装方法名均与官方api文档描述保持一致(除del外，del是python关键字，这里改成delete)
        . 所有api接口调用的第一个参数必须是access token，不管该api在官方文档里是否要求鉴权
        . 参数必须以命名参数的形式传递, 如：t.add(token, content = u'天朝SB一大堆，你抄我嘞我抄你。')。如果要传递字符串参数，请使用unicode。
        
        python版本要求：python2.6+，不支持python3.x
    
    example:
        import webbrowser
        
        init(app_key, app_secret)   # 设置AppKey和AppSecret(只需初始化一次)
        token = OAuthToken.get_request_token()  # 获取未授权的request token
        webbrowser.open(token.get_authorize_url())  # 进入用户授权页面
        verifier = raw_input("Input the verifier: ").strip() 
        token.set_verifier(verifier)    # 设置授权码，并自动换取access token
        t.add(token, content = u'天朝SB一大堆，你抄我嘞我抄你。') # 发微博
'''

__all__ = ['init', 'OAuthToken', 'statuses', 't', 'user', 'friends', 'private', 'search', 'trends', 'info', 'fav', 'ht', 'tag', 'other']
__version__ = '0.1a'
__author__ = 'darkbull'

import urllib
import time
import hashlib
import binascii
import random
import hmac
import json
import httplib
import uuid
import mimetypes
from os.path import getsize, isfile, basename
from urlparse import urlparse

APP_KEY = ''
APP_SECRET = ''

hmac_sha1 = lambda key, val: binascii.b2a_base64(hmac.new(key, val, hashlib.sha1).digest())[:-1]
nonce = lambda: str(random.randint(1000000, 9999999))
tm = lambda: str(int(time.time()))
utf8 = lambda u: u.encode('utf-8')
urlencode = lambda p: urllib.quote_plus(p, safe = '~')
# urldecode = lambda s: urllib.unquote_plus(s)

def init(app_key, app_secret):
    global APP_KEY, APP_SECRET
    APP_KEY, APP_SECRET = app_key, app_secret

class OAuthError(IOError):
    pass
    
class QWeiBoError(Exception):
    pass

# 错误码说明，参考：http://open.t.qq.com/resource.php?i=1,1#21_90
_ERROR_RET = [
        u'成功返回',        # ret = 0
        u'参数错误'         # ret = 1
        u'频率受限'         # ret = 2
        u'鉴权失败',        # ret = 3
        u'服务器内部错误',  # ret = 4
    ]
_ERROR_CODE = {
        (1, 4): u'脏话过多',
        (1, 5): u'禁止访问，如城市，uin黑名单限制等',
        (1, 6): u'删除时：该记录不存在。发表时：父节点已不存在',
        (1, 8): u'内容超过最大长度：420字节',
        (1, 9): u'包含垃圾信息：广告，恶意链接、黑名单号码等',
        (1, 10): u'发表太快，被频率限制',
        (1, 11): u'源消息已删除，如转播或回复时',
        (1, 12): u'源消息审核中',
        (1, 13): u'重复发表',
        
        (3, 1): u'无效TOKEN, 被吊销',
        (3, 2): u'请求重放',
        (3, 3): u'access_token不存在',
        (3, 4): u'access_token超时',
        (3, 5): u'oauth 版本不对', 
        (3, 6): u'oauth 签名方法不对',
        (3, 7): u'参数错',
        (3, 8): u'处理失败',
        (3, 9): u'验证签名失败',
        (3, 10): u'网络错误',
        (3, 11): u'参数长度不对',
        (3, 12): u'处理失败',
        (3, 13): u'处理失败',
        (3, 14): u'处理失败',
        (3, 15): u'处理失败',
        
        (4, 4): u'脏话过多',
        (4, 5): u'禁止访问，如城市，uin黑名单限制等',
        (4, 6): u'删除时：该记录不存在。发表时：父节点已不存在',
        (4, 8): u'内容超过最大长度：420字节 （以进行短url处理后的长度计）',
        (4, 9): u'包含垃圾信息：广告，恶意链接、黑名单号码等',
        (4, 10): u'发表太快，被频率限制',
        (4, 11): u'源消息已删除，如转播或回复时',
        (4, 12): u'源消息审核中',
        (4, 13): u'重复发表',
    }
    
def request(http_method, url, query = None, files = None):
    '''向远程服务器发送一个http request
    @param http_method: 请求方法
    @param url: 网址
    @param query: 提交的参数. dict: key: 表单域名称, value: 域值
    @param files: 上传的文件, dict: key: 表单域名称，value: 文件路径
    @return: 元组(response status, reason, response html)
    '''
    scheme, netloc, path, params, args = urlparse(url)[:5]
    conn = httplib.HTTPConnection(netloc) if scheme == 'http' else httplib.HTTPSConnection(netloc)
    headers = {
            'User-Agent': 'QQWeiBo-Python-Client;Created by darkbull(http://darkbull.net)',
            'Host': netloc,
        }
        
    if files:
        assert http_method == 'POST'
        boundary = '------' + str(uuid.uuid4())
        body = [ ]
        
        if query:
            for field_name, val in query.items():
                body.append('--' + boundary)
                body.append('Content-Disposition: form-data; name="%s"' % field_name)
                body.append('')
                body.append(val)
                
        for field_name, file in files.items():
            if not isfile(file) or getsize(file) / 1024 / 1024: # todo: file max size
                raise QWeiBoError, 'File "{0}" not exists, or it is too big, must be less than 1024KB.' % file
            mimetype = mimetypes.guess_type(file)[0]
            filename = basename(file)
            with open(file, 'rb') as f:
                data = f.read()
            body.append('--' + boundary)
            body.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (field_name, filename))
            if mimetype:
                body.append('Content-Type: ' + mimetype)
            body.append('Content-Transfer-Encoding: binary')
            body.append('')
            body.append(data)
        
        body.append('--' + boundary)
        body.append('')
        body = '\r\n'.join(body)
        headers['Content-Length'] = str(len(body))
        headers['Connection'] = 'keep-alive'
        headers['Content-Type'] = 'multipart/form-data; boundary=' + boundary
    else:
        body = urllib.urlencode(query) if query else ''
        if http_method == 'POST':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Content-Length'] = str(len(body))
        elif http_method == 'GET' and body:
            args = args + '&' + body if args else body
            body = None
                
    if args:
        path += '?' + args
    conn.request(http_method, path, body = body, headers = headers)  
    resp = conn.getresponse()
    result = (resp.status, resp.reason, resp.read())
    conn.close()
    return result
    
class OAuthToken(object):
    def __init__(self, token, secret, callback_confirmed):
        self.token = token
        self.secret = secret
        self.callback_confirmed = callback_confirmed
        self.verifier = ''
        self.name = ''
        self._authorized = 0
        
    def __str__(self):
        return '{token: %s, secret: %s, callback_confirmed: %s, verifier: %s, name: %s, authorized: %d}' % (self.token, self.secret, self.callback_confirmed, self.verifier, self.name, self._authorized)
    
    _SIGNATURE_BASE_STRING = ('GET', 'https://open.t.qq.com/cgi-bin/request_token', 'oauth_callback={callback}&oauth_consumer_key={app_key}&oauth_nonce={nonce}&oauth_signature_method=HMAC-SHA1&oauth_timestamp={timestamp}&oauth_version=1.0')
    _REQUEST_TOKEN_URL = 'https://open.t.qq.com/cgi-bin/request_token?oauth_callback={callback}&oauth_consumer_key={app_key}&oauth_nonce={nonce}&oauth_signature={signature}&oauth_signature_method=HMAC-SHA1&oauth_timestamp={timestamp}&oauth_version=1.0'
    @staticmethod
    def get_request_token(callback = 'null'):
        '''获取未授权的request token
        '''
        n, t, cbk = nonce(), tm(), urlencode(callback)
        http_method, uri, query = OAuthToken._SIGNATURE_BASE_STRING
        args = query.format(callback = cbk, app_key = APP_KEY, nonce = n, timestamp = t)
        sig_base_str = '&'.join(urlencode(item) for item in (http_method, uri, args))
        sig = hmac_sha1(APP_SECRET + '&', sig_base_str)
        url = OAuthToken._REQUEST_TOKEN_URL.format(callback = cbk, app_key = APP_KEY, nonce = n, signature = urlencode(sig), timestamp = t)
        try:
            errcode, reason, html = request(http_method, url)
        except IOError as ex:
            raise OAuthError(ex)
        if errcode != 200:
            raise OAuthError, (errcode, 'oauth error', reason)
        
        token, secret, confirm = (item.split('=')[1] for item in html.split('&'))
        return OAuthToken(token, secret, confirm)
        
    _AUTHORIZE_URL = 'https://open.t.qq.com/cgi-bin/authorize?oauth_token=%s'
    def get_authorize_url(self):
        '''获取用户授权url
        '''
        return OAuthToken._AUTHORIZE_URL % self.token
    
    def set_verifier(self, verifier):
        '''设置验证码。函数将自动换取access token.
        '''
        self.verifier = verifier
        self._get_access_token()
    
    _SIGNATURE_BASE_STRING2 = ('GET', 'https://open.t.qq.com/cgi-bin/access_token', 'oauth_consumer_key={app_key}&oauth_nonce={nonce}&oauth_signature_method=HMAC-SHA1&oauth_timestamp={timestamp}&oauth_token={token}&oauth_verifier={verifier}&oauth_version=1.0')
    _ACCESS_TOKEN_URL = 'https://open.t.qq.com/cgi-bin/access_token?oauth_consumer_key={app_key}&oauth_nonce={nonce}&oauth_signature_method=HMAC-SHA1&oauth_timestamp={timestamp}&oauth_token={token}&oauth_verifier={verifier}&oauth_version=1.0&oauth_signature={signature}'
    def _get_access_token(self):
        '''通过授权的request token换取access token
        '''
        if not self.verifier:
            raise OAuthError, ('oauth error', 'unauthorized request token.')
        if self._authorized:
            raise OAuthError, ('oauth error', 'token is already authorized.')
            
        n, t = nonce(), tm()
        http_method, uri, query = OAuthToken._SIGNATURE_BASE_STRING2
        args = query.format(app_key = APP_KEY, nonce = n, timestamp = t, token = self.token, verifier = self.verifier)
        sig_base_str = '&'.join(urlencode(item) for item in (http_method, uri, args))
        sig = hmac_sha1('%s&%s' % (APP_SECRET, self.secret), sig_base_str)
        url = OAuthToken._ACCESS_TOKEN_URL.format(app_key = APP_KEY, nonce = n, signature = urlencode(sig), timestamp = t, token = self.token, verifier = self.verifier)
        
        try:
            errcode, reason, html = request(http_method, url)
        except IOError as ex:
            raise OAuthError(ex)
        if errcode != 200:
            raise OAuthError, (errcode, 'oauth error', reason)
            
        self.token, self.secret, self.name = (item.split('=')[1] for item in html.split('&'))
        self._authorized = 1
            
    def to_header(self):
        if not self._authorized:
            raise OAuthError, ('oauth error', 'unauthorized token.')
        return { 
                'oauth_consumer_key': APP_KEY,
                'oauth_token': self.token,
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_timestamp': tm(),
                'oauth_nonce': nonce(),
                'oauth_version': '1.0',
                'format': 'json',   # NOTE: 通过json与服务器交互。在调用api时不允许再设置format参数
            }
        
class EntityBase(object):
    def __unicode__(self):
        return unicode(self.__dict__['___json_obj'])
        
    def __str__(self):
        return self.__unicode__().encode('utf-8')

class QWeiBoEntityList(EntityBase, list):
    pass

class QWeiBoEntity(EntityBase):
    pass
    
def json2entity(json_obj):
    tp = type(json_obj)
    if tp is dict:
        entity = QWeiBoEntity()
        entity.___json_obj = json_obj
        entity.__dict__.update(json_obj)
        for attr, val in json_obj.items():
            setattr(entity, attr, json2entity(val))
        return entity
    elif tp is list:
        entity = QWeiBoEntityList()
        entity.___json_obj = json_obj
        for item in json_obj:
            entity.append(json2entity(item))
        return entity
    elif tp is str:
        return json_obj.decode('utf-8')
    else:
        return json_obj
    
class API(object):
    _URI_COMMON = 'http://open.t.qq.com/api/'
    def __init__(self, http_method, uri, **kwargs):
        if not uri.startswith('http://') and not uri.startswith('https://'):
            uri = API._URI_COMMON + uri
        self.http_method = http_method.upper()
        self.uri = uri
        self.kwargs = kwargs
        self.uparams = [key for key, (optional, default, upload) in kwargs.items() if upload]    # 需要上传文件的参数
        
    def _call_api(self, token, params):
        upload_files = None
        if self.uparams:
            upload_files = { }
            for ukey in self.uparams:
                upload_files[ukey] = params[ukey]
                del params[ukey]
        items = list(params.items())
        items.sort()
        query = '&'.join(('%s=%s' % (urlencode(key), urlencode(val)) for key, val in items))
        sig_base_str = '%s&%s&%s' % (self.http_method, urlencode(self.uri), urlencode(query))
        sig = hmac_sha1('%s&%s' % (APP_SECRET, token.secret), sig_base_str)
        params['oauth_signature'] = sig
        try:
            errcode, reason, html = request(self.http_method, self.uri, params, upload_files)
        except IOError as ex:
            raise OAuthError(ex)
        if errcode != 200:
            raise QWeiBoError, 'errcode: %d, reason: %s' % (errcode, reason)
        return html
        
    def __call__(self, token, **kwargs):
        '''调用API。NOTE: 所有的字符串参数必须是unicode。例如：u'大家都懂的'
        '''
        for arg, (optional, default, upload) in self.kwargs.items():
            if not optional and arg not in kwargs and default is None:  # 必选参数没有默认值
                raise QWeiBoError, "parameter '%s' can't be empty." % arg
        for arg, (optional, default, upload) in self.kwargs.items():
            if not optional and arg not in kwargs:
                kwargs[arg] = default
        t = { }
        for key, val in kwargs.items():
            if type(key) is not unicode:
                key = unicode(key)
            if type(val) is not unicode:
                val = unicode(val)
            t[utf8(key)] = utf8(val)
        params = token.to_header()
        assert all(key not in params for key in t)
        params.update(t)
        response = self._call_api(token, params)
        response = response.decode('utf-8') # utf-8 => unicode
        result = json2entity(json.loads(response))
        if result.ret == 0:
            return result
        else:
            ret, errcode = result.ret, result.errcode
            if 0 <= ret <= 4:
                info = _ERROR_RET[ret]
            else:
                info = u'错误'    # fuck: 竟然出现在文档里未描述的错误码. 如短时间内连续两次发表同一张图片
            detail = _ERROR_CODE.get((ret, errcode, ))
            if not detail:
                detail = result.msg
            raise QWeiBoError, u'(ret: %s, errcode: %s)%s: %s' % (ret, errcode, info, detail)
        
    
# -------------------- API --------------------

parameter = lambda optional = False, default = None, upload = False: (optional, default, upload)
p = parameter

class Model(object):
    pass
    
statuses = Model()  # 时间线
statuses.home_timeline = API('GET', 'statuses/home_timeline', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 70), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.public_timeline = API('GET', 'statuses/public_timeline', pos = p(False, 0), reqnum = p(False, 100))
statuses.user_timeline = API('get', 'statuses/user_timeline', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 100), lastid = p(False, 0), name = p(False), type = p(True, 0), contenttype = p(True, 0), accesslevel = p(True))
statuses.mentions_timeline = API('GET', 'statuses/mentions_timeline', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 70), lastid = p(False, 0), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.ht_timeline = API('GET', 'statuses/ht_timeline', httext = p(False), pageflag = p(False, 4), pageinfo = p(False, ''), reqnum = p(False, 100))
statuses.broadcast_timeline = API('GET', 'statuses/broadcast_timeline', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 100), lastid = p(False, 0), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.special_timeline = API('GET', 'statuses/special_timeline', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 100), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.area_timeline = API('GET', 'statuses/area_timeline', pos = p(False, 0), reqnum = p(False, 100), country = p(False), province = p(False), city = p(False))
statuses.home_timeline_ids = API('GET', 'statuses/home_timeline_ids', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 300), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.user_timeline_ids = API('GET', 'statuses/user_timeline_ids', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 300), lastid = p(False, 0), name = p(False), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.broadcast_timeline_ids = API('GET', 'statuses/broadcast_timeline_ids', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 300), lastid = p(False, 0), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.mentions_timeline_ids = API('GET', 'statuses/mentions_timeline_ids', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 300), lastid = p(False, 0), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.users_timeline = API('GET', 'statuses/users_timeline', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 100), lastid = p(False, 0), names = p(False), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.users_timeline_ids = API('GET', 'statuses/users_timeline_ids', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 100), lastid = p(False, 0), names = p(False), type = p(False, 0), contenttype = p(False, 0), accesslevel = p(False, 1))
statuses.ht_timeline_ext = API('GET', 'statuses/ht_timeline_ext', reqnum = p(False, 50), pageflag = p(False, 0), flag = p(False, 0), accesslevel = p(False, 0), type = p(False, 1), contenttype = p(False, 0b111111), httext = p(False), htid = p(False, 0))
statuses.home_timeline_vip = API('GET', 'statuses/home_timeline_vip', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 70), lastid = p(False, 0))
    
t = Model() # 微博相关
t.show = API('GET', 't/show', id = p(False))
t.add = API('POST', 't/add', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True))
t.delete = API('POST', 't/del', id = p(False))  # t.del: del是python关键字
t.re_add = API('POST', 't/re_add', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True), reid = p(False))
t.reply = API('POST', 't/reply', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True), reid = p(False))
t.add_pic = API('POST', 't/add_pic', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True), pic = p(False, '', True), )
t.re_count = API('GET', 't/re_count', ids = p(False), flag = p(False, 0))
t.re_list = API('GET', 't/re_list', flag = p(False, 0), rootid = p(False), pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 20), twitterid = p(False, 0))
t.comment = API('POST', 't/comment', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True), reid = p(False))
t.add_music = API('POST', 't/add_music', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True), url = p(False), title = p(False), author = p(False))
t.add_video = API('POST', 't/add_video', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True), url = p(False))
t.getvideoinfo = API('POST', 't/getvideoinfo', url = p(False))  # 没错，文档里描述是post方式提交
t.list = API('GET', 't/list', ids = p(False))
t.add_video_prev = API('POST', 't/add_video_prev', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True), vid = p(False), title = p(False))
t.sub_re_count = API('GET', 't/sub_re_count', ids = p(False))

user = Model()  # 账户相关
user.info = API('GET', 'user/info')
user.update = API('POST', 'user/update', nick = p(False), sex = p(False, 0), year = p(False), month = p(False), day = p(False), countrycode = p(False), provincecode = p(False), citycode = p(False), introduction = p(False))
user.update_head = API('POST', 'user/update_head', pic = p(False, '', True))
user.update_edu = API('POST', 'user/update_edu', feildid = p(False), year = p(False), schoolid = p(False), departmentid = p(False), level = p(False))
user.other_info = API('GET', 'user/other_info', name = p(False))
user.infos = API('GET', 'user/infos', names = p(False))
user.verify = API('POST', 'user/verify', name = p(False))
user.emotion = API('POST', 'user/emotion', name = p(False), pageflag = p(False, 0), id = p(False, 0), timestamp = p(False, 0), type = p(False, 0), contenttype = p(False, 1), accesslevel = p(False, 0), emotiontype = p(False, 0xFFFFFFFF), reqnum = p(False, 70))

friends = Model()   # 关系链相关
friends.fanslist = API('GET', 'friends/fanslist', reqnum = p(False, 30), startindex = p(False, 0))
friends.idollist = API('GET', 'friends/idollist', reqnum = p(False, 30), startindex = p(False, 0))
friends.blacklist = API('GET', 'friends/blacklist', reqnum = p(False, 30), startindex = p(False, 0))
friends.speciallist = API('GET', 'friends/speciallist', reqnum = p(False, 30), startindex = p(False, 0))
friends.add = API('POST', 'friends/add', name = p(False))
friends.delete = API('POST', 'friends/del', name = p(False)) #friends.del: del是python关键字
friends.addspecial = API('POST', 'friends/addspecial', name = p(False))
friends.delspecial = API('POST', 'friends/delspecial', name = p(False))
friends.addblacklist = API('POST', 'friends/addblacklist', name = p(False))
friends.delblacklist = API('POST', 'friends/delblacklist', name = p(False))
friends.check = API('GET', 'friends/check', names = p(False), flag = p(False, 2))
friends.user_fanslist = API('GET', 'friends/user_fanslist', reqnum = p(False, 30), startindex = p(False, 0), name = p(False))
friends.user_idollist = API('GET', 'friends/user_idollist', reqnum = p(False, 30), startindex = p(False, 0), name = p(False))
friends.user_speciallist = API('GET', 'friends/user_speciallist', reqnum = p(False, 30), startindex = p(False, 0), name = p(False))
friends.fanslist_s = API('GET', 'friends/fanslist_s', reqnum = p(False, 200), startindex = p(False, 0))
friends.idollist_s = API('GET', 'friends/idollist_s', reqnum = p(False, 200), startindex = p(False, 0))
friends.mutual_list  = API('GET', 'friends/mutual_list ', name = p(False), startindex = p(False, 0), reqnum = p(False, 30))

private = Model()   # 私信相关
private.add = API('POST', 'private/add', content = p(False), clientip = p(False, '127.0.0.1'), jing = p(True), wei = p(True), name = p(False))
private.delete = API('POST', 'private/del', id = p(False))
private.recv = API('GET', 'private/recv', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 20), lastid = p(False, 0))
private.send = API('GET', 'private/send', pageflag = p(False, 0), pagetime = p(False, 0), reqnum = p(False, 20), lastid = p(False, 0))

search = Model()    # 搜索用户(合作者权限)
search.user = API('GET', 'search/user', keyword = p(False), pagesize = p(False), page = p(False))
search.t = API('GET', 'search/t', keyword = p(False), pagesize = p(False), page = p(False))
search.userbytag = API('GET', 'search/userbytag', keyword = p(False), pagesize = p(False), page = p(False))

trends = Model()    #热度，趋势
trends.ht = API('GET', 'trends/ht', type = p(False, 3), reqnum = p(False, 20), pos = p(False, 0))
trends.t = API('GET', 'trends/t', reqnum = p(False, 100), pos = p(False, 0))

info = Model()  # 数据更新相关
info.update = API('GET', 'info/update', op = p(False, 0), type = p(False, 5))   # 官方文档的参数说明让人摸不着头脑

fav = Model()   # 数据收藏
fav.addt = API('POST', 'fav/addt', type = p(False))
fav.delt = API('POST', 'fav/delt', type = p(False))
fav.list_t = API('GET', 'fav/list_t', pageflag = p(False, 0), nexttime = p(False, 0), prevtime = p(False, 0), reqnum = p(False, 20), lastid = p(False, 0))
fav.addht = API('POST', 'fav/addht', id = p(False))
fav.delht = API('POST', 'fav/delht', id = p(False))
fav.list_ht = API('GET', 'fav/list_ht', reqnum = p(False, 15), pageflag = p(False, 0), pagetime = p(False, 0), lastid = p(False, 0))

ht = Model()    # 话题相关
ht.ids = API('GET', 'ht/ids', httexts = p(False))
ht.info = API('GET', 'ht/info', ids = p(False))

tag = Model()   # 标签相关
tag.add = API('POST', 'tag/add', tag = p(False))
tag.delete = API('POST', 'tag/del', tagid = p(False))

other = Model() # 其他
other.kownperson = API('GET', 'other/kownperson')
other.shorturl = API('GET', 'other/shorturl', url = p(False))
other.videokey = API('GET', 'other/videokey')
other.get_emotions = API('GET', 'other/get_emotions', type = p(False))
other.gettopreadd = API('GET', 'other/gettopreadd', type = p(False))
