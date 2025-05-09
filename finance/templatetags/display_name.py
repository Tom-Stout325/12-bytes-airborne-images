from django import template

register = template.Library()

@register.filter
def get_by_id(queryset, value):
    try:
        return queryset.get(id=value)
    except:
        return ""
