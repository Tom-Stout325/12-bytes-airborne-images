from django import template

register = template.Library()

@register.filter
def duration_display(value):
    if value is None:
        return "0 minutes"

    total_seconds = int(value.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
