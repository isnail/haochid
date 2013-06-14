__author__ = 'biyanbing'
from django import template
from django.utils.importlib import import_module

register = template.Library()

@register.filter
def isinst(value, class_str):
    split = class_str.split('.')
    return isinstance(value, getattr(import_module('.'.join(split[:-1])), split[-1]))