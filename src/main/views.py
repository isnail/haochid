__author__ = 'biyanbing'

from django.http import Http404


def callback(req, plat):
    if plat not in ('s', 't'):
        raise Http404
    code = req.GET.get('code')

