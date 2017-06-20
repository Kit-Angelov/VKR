from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='author')
@stringfilter
def author(value): # Only one argument.
    """Converts a string into all lowercase"""
    return (value.replace('_', ' ')).title()


@register.filter(name='teaser')
@stringfilter
def teaser(value):
    return value[:100] + '...'
