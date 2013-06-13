
__author__ = 'biyanbing'

from functools import wraps

from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from utils import *

def login_required(response_type='redirect', redirect_to_view=None, sign_in_redirect_msg=None):
    def _decorator(func):
        @wraps(func)
        def _wrapped_func(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated():
                if request.is_ajax():
                    return JsonResponse({'status': -1, 'url': reverse('ajax_login')})
                return redirect('%s?next=%s' % (reverse('login'), request.get_full_path()))
            return func(request, *args, **kwargs)
        return _wrapped_func
    return _decorator