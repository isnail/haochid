__author__ = 'biyanbing'


from django.contrib.auth import authenticate, login as system_login, logout
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm

from forms import *
from plat.models import Plat
from models import *
from utils import *
import settings
from core.decorators import login_required

@csrf_exempt
def register(req):
    context = {}
    if req.method == 'POST':
        form = UserRegisterForm(req.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data.get('email'), form.cleaned_data.get('password'))
            user.email = form.cleaned_data.get('email')
            plat = Plat.objects.get(name='l')
            user.plat = plat
            user.ip = get_ip(req)
            user.save()
            user = authenticate(username=user.uid, password=form.cleaned_data.get('password'))
            system_login(req, user)
            return render(req, {}, 'registration/register_success.html')
    else:
        form = UserRegisterForm()
    context['form'] = form
    context['user'] = req.user
    context['title'] = cn_key._register
    return render(req, context, 'registration/register.html')

def logout(req):
    logout(req)
    if hasattr(req, 'user'):
        req.user = None
    return redirect(settings.LOGIN_REDIRECT_URL)

def ajax_login(req):
    if req.method == "POST":
        form = AuthenticationForm(data=req.POST)
        if form.is_valid():
            system_login(req, form.get_user())
            if req.session.test_cookie_worked():
                req.session.delete_test_cookie()
            return JsonResponse({'status': 1})
    return JsonResponse({'status': -1, 'error': True})


@login_required()
def account(req):
    user = req.user
    ctx = {'title': ''}
    if req.method == "POST":
        form = UserAccountForm(req.POST)
        if form.is_valid():
            ctx['success'] = True
            pass
        ctx['form'] = form
    else:
        ctx['form'] = UserAccountForm(instance=user)
    return render(req, ctx, 'user/account.html')


#
#
# def get_ip(req):
#     if req.META.has_key('HTTP_X_FORWARDED_FOR'):
#         ip =  req.META['HTTP_X_FORWARDED_FOR']
#     else:
#         ip = req.META.get('REMOTE_ADDR', '')
#     return ip
#
# def register(req):
#     if req.method == 'POST':
#         form = UserForm(req.POST)
#         if form.is_valid():
#             plat = Plat.objects.get(name='l')
#             user = User.objects.create_user(form.changed_data.get('email'), form.changed_data.get('email'),
#                                             form.changed_data.get('password'))
#             user_info = UserInfo.objects.create(system_user=user, plat=plat, uid=user.email, ip=get_ip(req))
#             login(req, user)
#             req.__class__.user_info = user_info
#         pass
#
#     return