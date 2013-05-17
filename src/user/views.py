__author__ = 'biyanbing'


from django.contrib.auth import authenticate, login as system_login
from django.views.decorators.csrf import csrf_exempt

from forms import *
from plat.models import Plat
from models import *
from utils import *

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
    else:
        form = UserRegisterForm()
    context['form'] = form
    context['user'] = req.user
    return render(req, context, 'registration/register.html')

def callback(req, plat):

    pass


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