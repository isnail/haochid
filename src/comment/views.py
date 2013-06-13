__author__ = 'biyanbing'

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from utils import *
from models import *
from forms import *


default_count = 10

@login_required
def comment_list(req, product_id):
    page = req.GET.get('page', 1)
    qs = Comment.objects.filter(product=product_id, parent=None)
    if not qs:
        raise Http404
    p, qs = paginator(qs, default_count, page)
    result = []
    for q in qs:
        children = Comment.objects.filter(parent=q, status=True).order_by('created_time')
        if not children and not q.status:
            pass
        else:
            data = q.to_dict(req.user)
            data['children'] = []
            for child in children:
                data['children'].append(child.to_dict(req.user))
            result.append(data)
        return JsonResponse({'status': 1, 'data': result, 'user': str(req.user), 'hasNext': qs.has_next()})


def comment_add(req):
    form = CommentAddForm(req.POST)
    user = req.user
    if form.is_valid():
        data = form.cleaned_data()
        data['user'] = user
        comment = Comment(data)
        if comment.is_send and user.plat.name in ('s', 't'):
            pass
        return JsonResponse({'status': 1, 'comment': comment.to_dict(user)})
    else:
        errors = form.errors
        return JsonResponse({'status': 0, 'errors': errors})


def comment_del(req):
    comment_id = req.GET.get('id', 0)
    comment = get_object_or_404(Comment, comment_id)
    if comment.user == req.user:
        if Comment.objects.filter(parent=comment):
            comment.status = False
            comment.save()
            return JsonResponse({'status': 1, 'delete': 0})
        else:
            comment.delete()
            return JsonResponse({'status': 1, 'delete': 1})
    return JsonResponse({'status': 0})
