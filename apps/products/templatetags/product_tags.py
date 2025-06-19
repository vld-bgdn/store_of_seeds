from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter
def format_difficulty(value):
    """Format difficulty level for display"""
    difficulty_map = {
        "easy": _("легкий"),
        "medium": _("средний"),
        "hard": _("тяжелый"),
    }
    return difficulty_map.get(value, value)
