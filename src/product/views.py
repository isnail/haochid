__author__ = 'biyanbing'
import datetime, urllib2, json, StringIO

from django.db import connection
from django.core.urlresolvers import reverse
from django.http import Http404
from django.core.cache import cache
from django.utils import timezone
from django.shortcuts import get_object_or_404

from utils import *
from product import models
from user.models import User
from core.decorators import login_required
import qrcode
import cn_key


default_count = 21
product_statistic_prefix = 'product_'
cache_timeout = 36 * 3600


def index(req):
    ctx = {}
    recommend = models.DailyRecommended.objects.all().order_by('-date')[:3]
    ctx['recommend'] = [_product_to_dict(r.product, req.user) for r in recommend]
    return render(req, ctx, 'index.html')


def categories(req):
    ctx = {}
    categories = models.Category.objects.all().order_by('name')
    if req.GET.get('alt') == 'json':
        ctx['status'] = 1
        data = []
        for c in categories:
            data.append({'id': c.id, 'name': c.name, 'url': reverse('category', kwargs={'id': c.id})})
        ctx['data'] = data
        return JsonResponse(ctx)
    ctx['data'] = categories
    return render(req, ctx, 'product/category-list.html')


def category(req, id):
    ctx = {}
    category = get_object_or_404(models.Category, id=id)
    recommend = models.DailyRecommended.objects.filter(product__category=category).order_by('-date')[:3]
    ctx['name'] = category.name
    ctx['id'] = category.id
    ctx['page_name'] = 'category'
    ctx['status'] = 1
    ctx['title'] = category.name
    ctx['recommend'] = [_product_to_dict(r.product, req.user) for r in recommend]
    if req.GET.get('alt') == 'json':
        return JsonResponse(ctx)
    return render(req, ctx, 'product/list.html')


def qr(req):
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
    )
    url = req.GET.get('url', '')
    url = '%s%s' % (req.get_host(), url)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img_buffer = StringIO.StringIO()
    img.save(img_buffer, format='JPEG')
    return HttpResponse(img_buffer.getvalue(), 'image/jpeg')


def category_products(req):
    ctx = {}
    category_id = req.GET.get('c')
    if not category_id:
        raise Http404
    category = get_object_or_404(models.Category, id=category_id)
    page = req.GET.get('page', 1)
    p, qs = paginator(models.Product.objects.filter(category=category), default_count, page)
    data = [_product_to_dict(q, req.user) for q in qs]
    ctx['data'] = {'products': data}
    ctx['hasNext'] = qs.has_next()
    ctx['status'] = 1
    return JsonResponse(ctx)


def _product_to_dict(product, user=None):
    result = product.to_dict()
    if user and isinstance(user, User):
        vote_track = models.VoteTrack.objects.filter(user=user, product=product).values('product_id', 'vote_status')
        if vote_track:
            vote_info = vote_track[0]
            result['vote_up'] = True if vote_info['vote_status'] == models.vote_status_choices[0][0] else False
            result['vote_down'] = True if vote_info['vote_status'] == models.vote_status_choices[1][0] else False
    return result


def _product_info(product, user=None):
    result = {'id': product.id}
    if user and isinstance(user, User):
        vote_track = models.VoteTrack.objects.filter(user=user, product=product).values('product_id', 'vote_status')
        if vote_track:
            vote_info = vote_track[0]
            result['vote_up'] = True if vote_info['vote_status'] == models.vote_status_choices[0][0] else False
            result['vote_down'] = True if vote_info['vote_status'] == models.vote_status_choices[1][0] else False
    return result


def get_daily(req, date=None):
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        date = None
    if not date:
        date = datetime.datetime.today()
    page = req.GET.get('page', 1)
    count = req.GET.get('count', default_count)
    try:
        count = int(count)
        if count < 1:
            count = default_count
    except:
        count = default_count
    if date:
        drps = models.DailyRecommended.objects.filter(date=date, product__status=models.product_status_choices[0][0])
    else:
        drps = models.DailyRecommended.objects.filter(product__status=models.product_status_choices[0][0])
    p, drps = paginator(drps, count, page)
    result = []
    for drp in drps:
        product_info = _product_to_dict(drp.product, req.user)
        product_info['reason'] = drp.reason
        result.append(product_info)
    return JsonResponse({'status': 1, 'data': result, 'hasNext': drps.has_next()})


def new(req, page=1):
    count = req.GET.get('count', default_count)
    try:
        count = int(count)
        if count < 1:
            count = default_count
    except:
        count = default_count
    products = models.Product.objects.filter(status=models.product_status_choices[0][0])
    p, qs = paginator(products, count, page)
    result = {'products': [_product_to_dict(q, req.user) for q in qs]}
    return JsonResponse({'status': 1, 'data': result, 'hasNext': qs.has_next()})


def new_index(req):
    ctx = {}
    ctx['name'] = cn_key._new
    ctx['page_name'] = 'new'
    ctx['title'] = cn_key._new
    return render(req, ctx, 'product/list.html')

def hot(req, page=1):
    count = req.GET.get('count', default_count)
    try:
        count = int(count)
        if count < 1:
            count = default_count
    except:
        count = default_count
    products = models.HotProduct.objects.filter(product__status='A')
    p, qs = paginator(products, count, page)
    result = {'products': [_product_to_dict(q.product, req.user) for q in qs]}
    return JsonResponse({'status': 1, 'data': result, 'hasNext': qs.has_next()})


def hot_index(req):
    ctx = {}
    ctx['name'] = cn_key._hot
    ctx['page_name'] = 'hot'
    ctx['title'] = cn_key._hot
    return render(req, ctx, 'product/list.html')



def product_info(req, id):
    product = get_object_or_404(models.Product, id=id)
    data = _product_info(product, req.user)
    data['statistic'] = get_product_cache(product)
    return JsonResponse({'status': 1, 'data': data})


def product(req, id):
    ctx = {}
    product = get_object_or_404(models.Product, id=id, status=models.product_status_choices[0][0])
    baidu_map_url = 'http://api.map.baidu.com/location/ip?ak=D406fa7556e0d44df4f21ecacc2ef843&ip='
    rs = urllib2.urlopen(baidu_map_url)
    rs_data = json.loads(rs.read())
    rs_data['content']['point']['x'] = float(rs_data['content']['point']['x']) / 20037508.34 * 180
    rs_data['content']['point']['y'] = float(rs_data['content']['point']['y']) / 20037508.34 * 180
    ctx['product'] = product
    ctx['map'] = rs_data
    ctx['title'] = product.title
    if req.GET.get('alt') == 'json':
        ctx['product'] = product.to_dict()
        ctx['status'] = 1
        return JsonResponse(ctx)
    return render(req, ctx, 'product/detail.html')


@login_required()
def vote(req, product_id, vote):
    if vote not in dict(models.vote_status_choices).keys():
        raise Http404()
    try:
        product = models.Product.objects.get(id=product_id)
        try:
            vote_track = models.VoteTrack.objects.get(user=req.user, product=product)
            old_status = vote_track.vote_status
            if old_status != vote:
                vote_track.vote_status = vote
                vote_track.save()
                if vote == models.vote_status_choices[2][0]:
                    # vote = cancel
                    if old_status == models.vote_status_choices[0][0]:
                        # old_status = up
                        update_cache(vote, product, -1)
                    else:
                        # old_status = down
                        update_cache(vote, product, -1)
                else:
                    if old_status != vote:
                        if old_status == models.vote_status_choices[0][0]:
                            update_cache(vote, product, -1)
                        else:
                            update_cache(vote, product, -1)
        except models.VoteTrack.DoesNotExist:
            models.VoteTrack.objects.create(user=req.user, product=product, vote_status=vote)
            if vote == models.vote_status_choices[0][0]:
                update_cache(vote, product, 1)
            elif vote == models.vote_status_choices[1][0]:
                update_cache(vote, product, 1)
        return JsonResponse('ok')
    except models.Product.DoesNotExist:
        raise Http404()


def get_product_cache(product):
    cache_key = '%s%s' % (product_statistic_prefix, product.id)
    cache_value = cache.get(cache_key)
    if not cache_value:
        cache_value = {'v': product.view_count, 's': product.share, 'u': product.vote_up, 'd': product.vote_down}
        cache.set(cache_key, cache_value, cache_timeout)
    return cache_value


def update_cache(s_type, product, point=0):
    if product.created_time + datetime.timedelta(days=30) > timezone.now():
        cache_key = '%s%s' % (product_statistic_prefix, product.id)
        cache_value = get_product_cache(product)
        cache_value[s_type] += 1
        cache.set(cache_key, cache_value, cache_timeout)
    else:
        if s_type == 's':
            product.increase_share()
        elif s_type == 'v':
            product.increase_view_count()
        elif s_type == 'u':
            product.increase_vote_up(point)
        elif s_type == 'd':
            product.increase_vote_down(point)



def _hot_cron():
    """
    create hot product per 3 hours
    """
    last_month_ago = datetime.datetime.now() - datetime.timedelta(days=31)
    products = models.Product.objects.filter(status=models.product_status_choices[0][0],
                                             create_time__gte=last_month_ago)
    for product in products:
        statistic = get_product_cache(product)
        product.share = statistic['s']
        product.vote_up = statistic['u']
        product.vote_down = statistic['d']
        product.view_count = statistic['v']
        product.save()

    sql = """
    truncate %(table)s;
    insert into %(table)s (product, score, created_time)
    select
    a.id,
    COALESCE((a.view_count + a.share * 10 + a.vote_up * 50 - a.vote_down) / LOG(2.718,
                    TIMESTAMPDIFF(HOUR, a.created_time, now())) + 1.001),
            0),
    now()
    from %(product)s a
    where a.create_time > '%(last_month_ago)s' and a.status='A';
    """
    sql = sql % {'table': models.HotProduct._meta.db_table, 'product': models.Product._meta.db_table,
                 'last_month_ago': last_month_ago}
    cursor = connection.cursor()
    cursor.execute(sql)
    pass

def hot_cron(req):
    _hot_cron()
    return HttpResponse('ok')