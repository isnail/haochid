__author__ = 'biyanbing'
import json, re

from django.contrib.sites.models import get_current_site
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render_to_response

# from user.models import UserInfo
from oss.oss_api import *
from settings import oss_host, access_id, secret_access_key, bucket
from user.models import User

def render(req, context, templates):
    context['user'] = req.user if isinstance(req.user, User) else None
    context['site_name'] = get_current_site(req).name
    return render_to_response(templates, context)

def get_ip(req):
    if req.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip =  req.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = req.META.get('REMOTE_ADDR', '')
    return ip


def JsonResponse(message):
    """
    :param status:  1   ok
                    0   error
                    -1  require login
    """
    return HttpResponse(json.dumps(message), mimetype='application/json')


def paginator(qs, count, page):
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


def replace_html_tags(html):
    return html.replace('<', '&lt;').replace('>', '&gt;')


def check_email(email):
    email_re = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
        r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'  # domain
        r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)
    if not email_re.search(email):
        return False
    return True