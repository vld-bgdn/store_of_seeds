from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter
def format_difficulty(value):
    """Format difficulty level for display"""
    difficulty_map = {
        "easy": _("Easy"),
        "medium": _("Medium"),
        "hard": _("Hard"),
    }
    return difficulty_map.get(value, value)
