from django.core.exceptions import ImproperlyConfigured

# from user.models import UserInfo
from django.middleware.common import CommonMiddleware

SESSION_KEY = '_auth_user_id'


# class LazyUser(object):
#     def __get__(self, request, obj_type=None):
#         if not hasattr(request, '_cached_user'):
#             user_id = request.session.get(SESSION_KEY, 0)
#             p = UserInfo.objects.filter(pk=user_id)
#             if p:
#                 request._cached_user = p[0]
#             else:
#                 request._cached_user = None
#         return request._cached_user
#
#     def __set__(self, request, value):
#         if isinstance(value, UserInfo) and hasattr(value, 'pk'):
#             request.session[SESSION_KEY] = int(value.pk)
#         elif isinstance(value, (long, int)) and UserInfo.objects.filter(pk=value).exists():
#             request.session[SESSION_KEY] = int(value)
#         elif not value and request.session.has_key(SESSION_KEY):
#             del request.session[SESSION_KEY]
#
#     def __delete__(self, request):
#         if request.session.has_key(SESSION_KEY):
#             del request.session[SESSION_KEY]


class UserAuthMiddleware(object):
    def process_request(self, request):
        # assert hasattr(request,
        #                'session'), "The Django authentication middleware requires session middleware \
        #                 to be installed. Edit your MIDDLEWARE_CLASSES setting to insert \
        #                 'django.contrib.sessions.middleware.SessionMiddleware'."
        # lp = LazyUser()
        # request.__class__.user = lp
        return None
