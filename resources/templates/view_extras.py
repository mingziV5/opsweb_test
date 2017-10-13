from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@stringfilter
def lower(value):
    return value.lower()

@register.filter(needs_autoescape = True)
def initial_letter_filter(text, autoescape=None):
    first, other = text[0], text[1:]
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    result = '<strong>%s</strong>%s' %(esc(first), esc(other))
    return mark_safe(result)

@register.filter(expects_localtime = True)
def businesshours(value):
    try:
        return 9<= value.hour < 17
    except AttributeError:
        return ''