__author__ = 'biyanbing'
import json
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from oss.oss_api import *


def JsonResponse(*args, **kwargs):
    if args:
        kwargs['message'] = args[0]
        kwargs['status'] = kwargs.get('status', 'error')
    return HttpResponse(json.dumps(kwargs), mimetype='application/json')


def page(qs, count, page):
    """ shortcut for get paged result, base on Paginator """
    p = Paginator(qs, count)
    try:
        objs = p.page(page)
    except PageNotAnInteger:
        objs = p.page(1)
    except EmptyPage:
        objs = p.page(p.num_pages)
    return p, objs


access_id = 'NtKMKCiLAiK8OlpV'
secret_access_key = 'Y6DEQhEhzgRzOJES5HdQZUFFj0rRsM'
oss_host = 'oss.aliyuncs.com'
bucket = 'haochid'


def save_to_oss(object, content):
    oss = OssAPI(oss_host, access_id, secret_access_key)
    oss.get_connection()
    oss.put_object_from_string(bucket, object, content)
    return 'http://%s/%s/%s' % (oss_host, bucket, object)
