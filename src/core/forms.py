__author__ = 'biyanbing'
# from django.forms import *
from django.utils.html import format_html, format_html_join
from django.utils.encoding import force_text, python_2_unicode_compatible


@python_2_unicode_compatible
class ErrorList(list):
    def __str__(self):
        return self.as_ul()

    def as_ul(self):
        if not self: return ''
        return format_html(u'<ul class="errorlist">{0}</ul>',
                           format_html_join('', u'<li><i class="icon-cancel-2"></i>{0}</li>',
                                            ((force_text(e),) for e in self)
                           )
        )

    def as_text(self):
        if not self: return ''
        return '\n'.join(['* %s' % force_text(e) for e in self])

    def __repr__(self):
        return repr([force_text(e) for e in self])
