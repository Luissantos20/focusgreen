from django import template

register = template.Library()

@register.filter
def format_minutes(value):
    """Formata minutos em formato legível (ex: 1h 20min, 45min)."""
    try:
        minutes = int(value)
    except (ValueError, TypeError):
        return value

    if minutes < 60:
        return f"{minutes} min"

    hours = minutes // 60
    remaining = minutes % 60
    if remaining:
        return f"{hours}h {remaining}min"
    return f"{hours}h"
