__author__ = 'biyanbing'
import json
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render_to_response

# from user.models import UserInfo
from oss.oss_api import *
from settings import oss_host, access_id, secret_access_key, bucket


def render(req, context, templates):

    return render_to_response(templates, context)

def get_ip(req):
    if req.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip =  req.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = req.META.get('REMOTE_ADDR', '')
    return ip


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


def save_to_oss(object, content, content_type):
    oss = OssAPI(oss_host, access_id, secret_access_key)
    oss.get_connection()
    oss.put_object_from_string(bucket, object, content, content_type)
    return '%s' % (object)
