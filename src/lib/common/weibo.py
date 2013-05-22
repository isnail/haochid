__author__ = 'biyanbing'

import gzip, time, hmac, base64, hashlib, urllib, urllib2, logging, mimetypes, collections, json, StringIO


class APIError(StandardError):
    '''
    raise APIError if receiving json message indicating failure.
    '''

    def __init__(self, error_code, error, request):
        self.error_code = error_code
        self.error = error
        self.request = request
        StandardError.__init__(self, error)

    def __str__(self):
        return 'APIError: %s: %s, request: %s' % (self.error_code, self.error, self.request)


class HttpObject(object):
    def __init__(self, client, method):
        self.client = client
        self.method = method

    def __getattr__(self, attr):
        def wrap(**kw):
            if self.client.is_expires():
                raise APIError('21327', 'expired_token', attr)
            return _http_call('%s%s.json' % (self.client.api_url, attr.replace('__', '/')), self.method,
                              self.client.access_token, **kw)

        return wrap


_HTTP_GET = 0
_HTTP_POST = 1
_HTTP_UPLOAD = 2


def _http_get(url, authorization=None, **kw):
    logging.info('GET %s' % url)
    return _http_call(url, _HTTP_GET, authorization, **kw)


def _http_post(url, authorization=None, **kw):
    logging.info('POST %s' % url)
    return _http_call(url, _HTTP_POST, authorization, **kw)


def _http_upload(url, authorization=None, **kw):
    logging.info('MULTIPART POST %s' % url)
    return _http_call(url, _HTTP_UPLOAD, authorization, **kw)


def _read_body(obj):
    using_gzip = obj.headers.get('Content-Encoding', '') == 'gzip'
    body = obj.read()
    if using_gzip:
        logging.info('gzip content received.')
        gzipper = gzip.GzipFile(fileobj=StringIO(body))
        fcontent = gzipper.read()
        gzipper.close()
        return fcontent
    return body

def _encode_multipart(**kw):
    ' build a multipart/form-data body with randomly generated boundary '
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    for k, v in kw.iteritems():
        data.append('--%s' % boundary)
        if hasattr(v, 'read'):
            # file-like object:
            filename = getattr(v, 'name', '')
            content = v.read()
            data.append('Content-Disposition: form-data; name="%s"; filename="hidden"' % k)
            data.append('Content-Length: %d' % len(content))
            data.append('Content-Type: %s\r\n' % _guess_content_type(filename))
            data.append(content)
        else:
            data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
            data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
    data.append('--%s--\r\n' % boundary)
    return '\r\n'.join(data), boundary


def _encode_params(**kw):
    '''
    do url-encode parameters

    >>> _encode_params(a=1, b='R&D')
    'a=1&b=R%26D'
    >>> _encode_params(a=u'\u4e2d\u6587', b=['A', 'B', 123])
    'a=%E4%B8%AD%E6%96%87&b=A&b=B&b=123'
    '''
    args = []
    for k, v in kw.iteritems():
        if isinstance(v, basestring):
            qv = v.encode('utf-8') if isinstance(v, unicode) else v
            args.append('%s=%s' % (k, urllib.quote(qv)))
        elif isinstance(v, collections.Iterable):
            for i in v:
                qv = i.encode('utf-8') if isinstance(i, unicode) else str(i)
                args.append('%s=%s' % (k, urllib.quote(qv)))
        else:
            qv = str(v)
            args.append('%s=%s' % (k, urllib.quote(qv)))
    return '&'.join(args)


def _decode_params(string):
    return dict(((v.split('=')[0].strip(), v.split('=')[1].strip()) for v in string.split('&')))


def _parse_json(s):
    ' parse str into JsonDict '

    def _obj_hook(pairs):
        ' convert json object to python object '
        o = JsonDict()
        for k, v in pairs.iteritems():
            o[str(k)] = v
        return o
    return json.loads(s, object_hook=_obj_hook)

class JsonDict(dict):
    ' general json object that allows attributes to be bound to and also behaves like a dict '

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(r"'JsonDict' object has no attribute '%s'" % attr)

    def __setattr__(self, attr, value):
        self[attr] = value


def _http_call(the_url, method, authorization, **kw):
    '''
    send an http request and return a json object if no error occurred.
    '''
    params = None
    boundary = None
    plat = kw.pop('plat')

    if method == _HTTP_UPLOAD and plat == 's':
        # fix sina upload url:
        the_url = the_url.replace('https://api.', 'https://upload.api.')
        params, boundary = _encode_multipart(**kw)
    else:
        params = _encode_params(**kw)
        if '/remind/' in the_url:
            # fix sina remind api:
            the_url = the_url.replace('https://api.', 'https://rm.api.')
    http_url = '%s?%s' % (the_url, params) if method == _HTTP_GET else the_url
    http_body = None if method == _HTTP_GET else params
    req = urllib2.Request(http_url, data=http_body)
    req.add_header('Accept-Encoding', 'gzip')
    if authorization:
        req.add_header('Authorization', 'OAuth2 %s' % authorization)
    if boundary:
        req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    try:
        resp = urllib2.urlopen(req)
        body = _read_body(resp)
        if plat == 't' and not kw.get('format') == 'json':
            body = json.dumps(_decode_params(body))
        r = _parse_json(body)
        if hasattr(r, 'error_code'):
            raise APIError(r.error_code, r.get('error', ''), r.get('request', ''))
        return r
    except urllib2.HTTPError, e:
        try:
            r = _parse_json(_read_body(e))
        except:
            r = None
        if hasattr(r, 'error_code'):
            raise APIError(r.error_code, r.get('error', ''), r.get('request', ''))
        raise e


class Api(object):
    def __init__(self, app_key, app_secret, type, redirect_uri, response_type='code'):
        self.client_id = str(app_key)
        self.client_secret = str(app_secret)
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.type = type
        self.access_token = ''
        self.auth_url = 'https://api.weibo.com/oauth2/' if self.type == 's' else 'https://open.t.qq.com/cgi-bin/oauth2/'
        self.api_url = 'https://api.weibo.com/2/' if self.type == 's' else 'http://open.t.qq.com/api/'
        self.get = HttpObject(self, _HTTP_GET)
        self.post = HttpObject(self, _HTTP_POST)
        self.upload = HttpObject(self, _HTTP_UPLOAD)
        # for tencent
        self.ip = ''
        self.openid = ''
        self.openkey = ''
        self.oauth_version = '2.a'
        self.format = 'json'


    def set_access_token(self, access_token, expires, openid='', openkey='', ip=''):
        self.access_token = str(access_token)
        self.expires = float(expires)
        self.ip = ip
        self.openid = openid
        self.openkey = openkey


    def request_access_token(self, code, redirect_uri=None):
        '''
        return access token as a JsonDict: {"access_token":"your-access-token","expires_in":12345678,"uid":1234}, expires_in is represented using standard unix-epoch-time
        '''
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        if not redirect:
            raise APIError('21305', 'Parameter absent: redirect_uri', 'OAuth2 request')

        r = _http_post('%s%s' % (self.auth_url, 'access_token'),
                       plat='s',
                       client_id = self.client_id,
                       client_secret = self.client_secret,
                       redirect_uri = redirect,
                       code = code,
                       grant_type = 'authorization_code')
        current = int(time.time())
        expires = int(r.expires_in) + current
        remind_in = r.get('remind_in', None)
        if remind_in:
            rtime = int(remind_in) + current
            if rtime < expires:
                expires = rtime
        return JsonDict(access_token=r.access_token, expires=expires, expires_in=expires)


    def refresh_token(self, refresh_token):
        req_str = '%s%s' % (self.auth_url, 'access_token')
        r = _http_post(req_str, \
            client_id = self.client_id, \
            client_secret = self.client_secret, \
            refresh_token = refresh_token, \
            grant_type = 'refresh_token')
        current = int(time.time())
        expires = r.expires_in + current
        remind_in = r.get('remind_in', None)
        if remind_in:
            rtime = int(remind_in) + current
            if rtime < expires:
                expires = rtime
        return JsonDict(access_token=r.access_token, expires=expires, expires_in=expires, uid=r.get('uid', None))

    def is_expires(self):
        return not self.access_token or time.time() > self.expires

    def __getattr__(self, attr):
        if '__' in attr:
            return getattr(self.get, attr)
        return _Callable(self, attr)


_METHOD_MAP = { 'GET': _HTTP_GET, 'POST': _HTTP_POST, 'UPLOAD': _HTTP_UPLOAD }

class _Executable(object):

    def __init__(self, client, method, path):
        self._client = client
        self._method = method
        self._path = path

    def __call__(self, **kw):
        method = _METHOD_MAP[self._method]
        if method==_HTTP_POST and 'pic' in kw:
            method = _HTTP_UPLOAD
        if self._client.access_token and self._client.plat == 't':
            kw['oauth_consumer_key'] = self._client.client_id
            kw['access_token'] = self._client.access_token
            kw['openid'] = self._client.open_id
            kw['clientip'] = self._client.ip
            kw['oauth_version'] = self._client.oauth_version
            kw['format'] = 'json'
        if self._client.plat == 't':
            return _http_call('%s%s' % (self._client.api_url, self._path), method, self._client.access_token, **kw)
        else:
            return _http_call('%s%s.json' % (self._client.api_url, self._path), method, self._client.access_token, **kw)

    def __str__(self):
        return '_Executable (%s %s)' % (self._method, self._path)

    __repr__ = __str__

class _Callable(object):

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, attr):
        if attr=='get':
            return _Executable(self._client, 'GET', self._name)
        if attr=='post':
            return _Executable(self._client, 'POST', self._name)
        name = '%s/%s' % (self._name, attr)
        return _Callable(self._client, name)

    def __str__(self):
        return '_Callable (%s)' % self._name

    __repr__ = __str__


sina = Api('key', 'secret', 'redirect_url', 's', 'https://api.weibo.com/oauth2/', 'https://api.weibo.com/2/')
tencent = Api('key', 'secret', 'redirect_url', 't', 'https://open.t.qq.com/cgi-bin/oauth2/authorize', 'api_url')