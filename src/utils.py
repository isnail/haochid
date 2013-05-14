__author__ = 'biyanbing'
import json
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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