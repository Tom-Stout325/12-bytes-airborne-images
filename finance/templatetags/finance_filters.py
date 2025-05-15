from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    return dictionary.get(key, 0)  # Return 0 if key is missing