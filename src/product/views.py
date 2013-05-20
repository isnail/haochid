__author__ = 'biyanbing'
import datetime, urllib2, json, StringIO

from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.http import Http404

from utils import *
import models
import qrcode


def index(req):
    # todo set cookies
    ctx = {}

    return render_to_response('index.html', ctx)


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


default_count = 21


def category(req, id):
    ctx = {}
    try:
        category = models.Category.objects.get(id=id)
        recommend = models.DailyRecommended.objects.filter(product__category=category).order_by('-date')[:3]
        ctx['name'] = category.name
        ctx['id'] = category.id
        ctx['status'] = 1
        ctx['recommend'] = [_product_to_dict(r.product, req.user) for r in recommend]
        if req.GET.get('alt') == 'json':
            return JsonResponse(ctx)
        return render(req, ctx, 'product/category.html')
    except models.Category.DoesNotExist:
        raise Http404


def qr(req):
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
    )
    url = req.GET.get('url', '')
    url = '%s/%s' % (req.get_host(), url)
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
    try:
        category = models.Category.objects.get(id=category_id)
        page = req.GET.get('page', 1)
        p, qs = paginator(models.Product.objects.filter(category=category), default_count, page)
        data = [_product_to_dict(q, req.user) for q in qs]
        ctx['data'] = data
        ctx['hasNext'] = qs.has_next()
        ctx['status'] = 1
        return JsonResponse(ctx)
    except models.Category.DoesNotExist:
        raise Http404


def _product_to_dict(product, user=None):
    result = product.to_dict()
    if user:
        vote_track = models.VoteTrack.objects.filter(user=user, product=product).values('product_id')
        if vote_track:
            vote_info = vote_track[0]
            result['vote_up'] = True if vote_info.vote_status == models.vote_status_choices[0][0] else False
            result['vote_down'] = True if vote_info.vote_status == models.vote_status_choices[1][0] else False
    return result


def _product_info(product, user=None):
    result = {'id': product.id}
    if user:
        vote_track = models.VoteTrack.objects.filter(user=user, product=product).values('product_id')
        if vote_track:
            vote_info = vote_track[0]
            result['vote_up'] = True if vote_info.vote_status == models.vote_status_choices[0][0] else False
            result['vote_down'] = True if vote_info.vote_status == models.vote_status_choices[1][0] else False
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


def new(req):
    page = req.GET.get('page', 1)
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


def product_info(req, id):
    try:
        product = models.Product.objects.get(id=id)
        data = _product_info(product, req.user)
        return JsonResponse({'status': 1, 'data': data})
    except:
        raise Http404


def product(req, id):
    ctx = {}
    try:
        product = models.Product.objects.get(id=id, status=models.product_status_choices[0][0])
        ctx['product'] = product

        baidu_map_url = 'http://api.map.baidu.com/location/ip?ak=D406fa7556e0d44df4f21ecacc2ef843&ip='
        rs = urllib2.urlopen(baidu_map_url)
        rs_data = json.loads(rs.read())
        print rs_data
        rs_data['content']['point']['x'] = float(rs_data['content']['point']['x']) / 20037508.34 * 180
        rs_data['content']['point']['y'] = float(rs_data['content']['point']['y']) / 20037508.34 * 180
        ctx['map'] = rs_data
        if req.GET.get('alt') == 'json':
            ctx['product'] = product.to_dict()
            ctx['status'] = 1
            return JsonResponse(ctx)
        return render(req, ctx, 'product/detail.html')
    except models.Product.DoesNotExist:
        raise Http404


def vote(req, product_id, vote):
    if not req.user:
        return JsonResponse({'status': -1})
    try:
        product = models.Product.objects.get(id=product_id)
        try:
            vote_track = models.VoteTrack.objects.get(user=req.user, product=product)
            old_status = vote_track.vote_status
            if old_status != vote:
                vote_track.vote_status = vote
                vote_track.save()
            if vote == models.vote_status_choices[2][0]:
                if old_status == models.vote_status_choices[0][0]:
                    product.increase_vote_up(-1)
                else:
                    product.increase_vote_down(-1)
            else:
                if old_status != vote:
                    if old_status == models.vote_status_choices[0][0]:
                        product.increase_vote_up(-1)
                    else:
                        product.increase_vote_down(-1)
        except models.VoteTrack.DoesNotExist:
            models.VoteTrack.objects.create(user=req.user, product=product, vote_status=vote)
            if vote == models.vote_status_choices[0][0]:
                product.increase_vote_up(1)
            elif vote == models.vote_status_choices[1][0]:
                product.increase_vote_down(1)
        return JsonResponse('ok')
    except models.Product.DoesNotExist:
        raise Http404()


