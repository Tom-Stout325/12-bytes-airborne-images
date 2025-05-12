from django import template
from datetime import date


register = template.Library()

@register.filter
def until(value, max_value):
    return range(value, max_value)

@register.filter
def to_int(value):
    return int(value)


@register.simple_tag
def month_choices():
    return [(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
