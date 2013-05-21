#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.0'
__author__ = 'hellophp(hellophp@qq.com)'

'''
Python client SDK for qq weibo API using OAuth 1.0
'''

try:
    import json
except ImportError:
    import simplejson as json
import time
import hmac
import uuid
import base64
import urllib
import urllib2
import hashlib
import mimetypes
#import logging

_OAUTH_SIGN_METHOD = 'HMAC-SHA1'
_OAUTH_VERSION = '1.0'

class OAuthToken(object):

    def __init__(self, oauth_token, oauth_token_secret, oauth_verifier=None, **kw):
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.oauth_verifier = oauth_verifier
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def __str__(self):
        attrs = [s for s in dir(self) if not s.startswith('__')]
        kvs = ['%s = %s' % (k, getattr(self, k)) for k in attrs]
        return ', '.join(kvs)

    __repr__ = __str__

class APIClient(object):
    def __init__(self, app_key, app_secret, domain='open.t.qq.com'):
        self.app_key = app_key
        self.app_secret = app_secret
        self.oauth_token = None
        self.oauth_token_secret = None
        self.oauth_verifier = None
        self.callback = None
        self.api_url = 'http://%s' % domain
        
    
    def set_client(self, app_key, app_secret, token = None, callback = None):
        self.app_key = str(app_key)
        self.app_secret = str(app_secret)
        self.callback = callback
        if token:
            if isinstance(token, OAuthToken):
                if token.oauth_token:
                    self.oauth_token = token.oauth_token
                if token.oauth_token_secret:
                    self.oauth_token_secret = token.oauth_token_secret
                if token.oauth_verifier:
                    self.oauth_verifier = token.oauth_verifier
            else:
                raise TypeError('token parameter must be instance of OAuthToken.')
        else:
            self.oauth_token = None
        self.get = HttpObject(self, _HTTP_GET)
        self.post = HttpObject(self, _HTTP_POST)
        self.upload = HttpObject(self, _HTTP_UPLOAD)
         
    def _oauth_request(self, method, url, **kw):
        params = dict( \
                oauth_consumer_key=self.app_key, \
                oauth_nonce=_generate_nonce(), \
                oauth_signature_method=_OAUTH_SIGN_METHOD, \
                oauth_timestamp=str(int(time.time())), \
                oauth_version=_OAUTH_VERSION, \
                oauth_token=self.oauth_token)
        params.update(kw)
        if params.has_key('pic'):
            params.pop('pic')
        m = 'GET' if method==_HTTP_GET else 'POST'
        bs = _generate_base_string(m, url, **params)
        key = '%s&%s' % (self.app_secret, self.oauth_token_secret)
        oauth_signature = _generate_signature(key, bs)
        #print 'params:', params
        #print 'base string:', bs
        #print 'key:', key, 'sign:', oauth_signature
        #print 'url:', url
        authorization = self.__build_oauth_parms(params, oauth_signature=oauth_signature)
        r = _http_call(url, method, authorization, return_json=True, **kw)
        return r

    def get_request_token(self):
        params = dict(
                oauth_callback=self.callback, \
                oauth_consumer_key=self.app_key, \
                oauth_nonce=_generate_nonce(), \
                oauth_signature_method=_OAUTH_SIGN_METHOD, \
                oauth_timestamp=str(int(time.time())), \
                oauth_version=_OAUTH_VERSION)
        url = '%s/cgi-bin/request_token' % self.api_url
        bs = _generate_base_string('GET', url, **params)
        params['oauth_signature'] = base64.b64encode(hmac.new('%s&' % self.app_secret, bs, hashlib.sha1).digest())
        r = _http_call(url, _HTTP_GET, return_json=False, **params)
        kw = _parse_params(r, False)
        return OAuthToken(**kw)

    def get_authorize_url(self, oauth_token):
        return '%s/cgi-bin/authorize?oauth_token=%s' % (self.api_url, oauth_token)

    def get_access_token(self):
        params = {
            'oauth_consumer_key': self.app_key,
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': _generate_nonce(),
            'oauth_version': _OAUTH_VERSION,
            'oauth_signature_method': _OAUTH_SIGN_METHOD,
            'oauth_token': self.oauth_token,
            'oauth_verifier': self.oauth_verifier,
        }
        url = '%s/cgi-bin/access_token' % self.api_url
        bs = _generate_base_string('GET', url, **params)
        key = '%s&%s' % (self.app_secret, self.oauth_token_secret)
        oauth_signature = _generate_signature(key, bs)
        authorization = self.__build_oauth_parms(params, oauth_signature=oauth_signature)
        r = _http_call(url, _HTTP_GET, authorization, return_json=False)
        kw = _parse_params(r, False)
        return OAuthToken(**kw) 

    def __build_oauth_parms(self, params, **kw):
        d = dict(**kw)
        d.update(params)
        L = [r'%s=%s' % (k, v) for k, v in d.iteritems() if k.startswith('oauth_')]
        return '%s' % '&'.join(L)

    def __getattr__(self, attr):
        ' a shortcut for client.get.funcall() to client.funcall() '
        return getattr(self.get, attr)

class APIError(StandardError):
    '''
    raise APIError if got failed json message.
    '''
    def __init__(self, errcode, msg):
        self._code = errcode
        self._msg = msg
        StandardError.__init__(self, msg)

    def __str__(self):
        return 'APIError: %s: %s' % (self._code, self._msg)
   
def _pack_image(authorization, filename, contentname, max_size=1024, **params):
    """Pack image from file into multipart-formdata post body"""
    # image must be less than 700kb in size
    params = dict(authorization, **params)
    
    # image must be gif, jpeg, or png
    file_type = mimetypes.guess_type(filename)
    if file_type is None:
        print('Could not determine file type')
    file_type = file_type[0]
    if file_type.split('/')[0] != 'image':
        print('Invalid file type for image: %s' % file_type)

    # build the mulitpart-formdata body
    boundary = '----------%s' % hex(int(time.time() * 1000))
    body = []
    for key, val in params.items():
        if val is not None:
            body.append('--' + boundary)
            body.append('Content-Disposition: form-data; name="%s"' % key)
            body.append('Content-Type: text/plain; charset=UTF-8')
            body.append('Content-Transfer-Encoding: 8bit')
            body.append('')
            val = convert_to_utf8_bytes(val)
            body.append(val)
    fp = open(filename, 'rb')
    body.append('--' + boundary)
    body.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (contentname, filename))
    body.append('Content-Type: %s' % file_type)
    body.append('Content-Transfer-Encoding: binary')
    body.append('')
    body.append(fp.read())
    body.append('--%s--' % boundary)
    body.append('')
    fp.close()
    body.append('--%s--' % boundary)
    body.append('')
    # fix py3k
    for i in range(len(body)):
        body[i] = convert_to_utf8_bytes(body[i])
    body = b'\r\n'.join(body)
    # build headers
    headers = {
        'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
        'Content-Length': len(body)
    }

    return headers, body

_HTTP_GET = 0
_HTTP_POST = 1
_HTTP_UPLOAD = 2

def _http_call(url, method, authorization=None, return_json=True, **kw):
    '''
    send an http request and return headers and body if no error.
    '''
    params = None
    headers = None
    if method == _HTTP_UPLOAD:
        kw = dict(**kw)
        if kw.has_key('pic'):
            filename = kw['pic']
        if kw.has_key('content'):
            content = kw['content']
        if kw.has_key('clientip'):
            clientip = kw['clientip']
        contentname = 'pic'
        headers, params = _pack_image(_parse_params(authorization), filename, contentname=contentname, content=content, clientip=clientip, jing=None, wei=None)
    else:
        params = _encode_params(**kw)
    
    if method==_HTTP_GET:
        http_url = '%s?%s' % (url, authorization)
        if params:
            http_url = '%s&%s' % (http_url, params)
        http_body = None
    elif method ==_HTTP_POST:
        http_url = '%s' % url
        http_body = '%s' % authorization
        if params:
            http_body = '%s&%s' % ( http_body, params)
    elif method ==_HTTP_UPLOAD:
        http_url = '%s' % url
        http_body = '%s' % params
    else:
        http_url = '%s?%s' % (url, authorization)
        http_body = None
  
    req = urllib2.Request(http_url, data=http_body)
    if headers:
        for k,v in headers.items():
            req.add_header(k, v)
    #print http_url
    #print 'method',method
    #print 'BODY:', http_body
    resp = urllib2.urlopen(req)
    body = resp.read()
    #print "resultbody:",body
    body = convert_to_utf8_bytes(body)
    if return_json:
        r = json.loads(body, object_hook=_obj_hook)
        if r.ret != 0:
            raise APIError(r.errcode, r.msg)
        return r
    return body

class HttpObject(object):

    def __init__(self, client, method):
        self.client = client
        self.method = method

    def __getattr__(self, attr):
        def wrap(**kw):
            return self.client._oauth_request(self.method, '%s/api/%s' % (self.client.api_url, attr.replace('__', '/')), **kw)
        return wrap

################################################################################
# utility functions
################################################################################

def _parse_params(params_str, unicode_value=True):
    '''
    parse a query string as JsonObject (also a dict)
    '''
    d = dict()
    for s in params_str.split('&'):
        n = s.find('=')
        if n>0:
            key = s[:n]
            value = urllib.unquote(s[n+1:])
            d[key] = value.decode('utf-8') if unicode_value else value
    return JsonObject(**d)

def _encode_params(**kw):
    '''
    Encode parameters.
    '''
    if kw:
        args = []
        for k, v in kw.iteritems():
            qv = v.encode('utf-8') if isinstance(v, unicode) else str(v)
            args.append('%s=%s' % (k, _quote(qv)))
        return '&'.join(args)
    return ''

def _quote(s):
    '''
    quote everything including
    '''
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return urllib.quote(str(s), safe='')

def _generate_nonce():
    ' generate random uuid as oauth_nonce '
    return uuid.uuid4().hex

def _generate_signature(key, base_string):
    '''
    generate url-encoded oauth_signature with HMAC-SHA1
    '''
    return base64.b64encode(hmac.new(key, base_string, hashlib.sha1).digest())

def _generate_base_string(method, url, **params):
    '''
    generate base string for signature
    '''
    plist = [(_quote(k), _quote(v)) for k, v in params.iteritems()]
    plist.sort()
    return '%s&%s&%s' % (method, _quote(url), _quote('&'.join(['%s=%s' % (k, v) for k, v in plist])))

def convert_to_utf8_str(arg):
    # return py2str py3str
    # fix py26
    MAJOR_VERSION = 2
    if MAJOR_VERSION == 3:
        unicodeType = str
        if type(arg) == unicodeType:
            return arg
        elif type(arg) == bytes:
            return arg.decode('utf-8')
    else:
        unicodeType = __builtins__['unicode']
        if type(arg) == unicodeType:
            return arg.encode('utf-8')
        elif type(arg) == str:
            return arg
    # assume list
    if hasattr(arg, '__iter__'):
        arg = ','.join(map(convert_to_utf8_str, arg))
    return str(arg)


def convert_to_utf8_bytes(arg):
    # return py2str py3bytes
    if type(arg) == bytes:
        return arg
    ret = convert_to_utf8_str(arg)
    return ret.encode('utf-8')

class JsonObject(dict):
    '''
    general json object that can bind any fields but also act as a dict.
    '''
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
        
def _obj_hook(pairs):
    '''
    convert json object to python object.
    '''
    o = JsonObject()
    for k, v in pairs.iteritems():
        o[str(k)] = v
    return o


