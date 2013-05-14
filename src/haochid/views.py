__author__ = 'biyanbing'
import datetime

from django.shortcuts import render_to_response

from utils import *
import models


def index(req):
    # todo set cookies
    ctx = {}
    return render_to_response('index.html', ctx)


def _product_to_dict(product, user=None):
    result = product.to_dict()
    if user:
        vote_track = models.VoteTrack.objects.filter(user=user, product=product).values('product_id')
        if vote_track:
            vote_info = vote_track[0]
            result['vote_up'] = True if vote_info.vote_status == models.vote_status_choices[0][0] else False
            result['vote_down'] = True if vote_info.vote_status == models.vote_status_choices[1][0] else False
    return result


default_count = 20


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
        page = int(page)
    except:
        page = 1
    try:
        count = int(count)
    except:
        count = default_count
    drps = models.DailyRecommended.objects.filter(date=date, product__status=models.product_status_choices[0][0])
    p, drps = page(drps, count, page)
    result = []
    for drp in drps:
        product_info = _product_to_dict(drp.product, req.user)
        product_info['reason'] = drp.reason
        result.append(product_info)
    return JsonResponse({'status': 'ok', 'data': result, 'count': p.count, 'page_nums': p.page_nums})


def new(req):
    page = req.GET.get('page', 1)
    count = req.GET.get('count', default_count)
    try:
        page = int(page)
    except:
        page = 1
    try:
        count = int(count)
    except:
        count = default_count
    products = models.Product.objects.filter(status=models.product_status_choices[0][0])
    p, qs = page(products, count, page)
    result = {'products': [_product_to_dict(q, req.user) for q in qs]}
    return JsonResponse({'status': 'ok', 'data': result, 'count': p.count, 'page_nums': p.page_nums})


def product_info(req, id):
    try:
        product = models.Product.objects.get(id=id)
        data = _product_to_dict(product, req.user)
        data['content'] = product.content
        return JsonResponse({'status': 'ok', 'data': data})
    except:
        return JsonResponse({'status': 'error'})


def product(req, id):
    # todo set cookies
    return render_to_response()


def vote(req, product_id, vote):
    if not req.user:
        return JsonResponse({'status': 'error'})
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
        return JsonResponse({'status': 'error'})


