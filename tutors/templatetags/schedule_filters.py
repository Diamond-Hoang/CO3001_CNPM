# tutors/templatetags/schedule_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary:
        return dictionary.get(key)
    return None

@register.filter
def index(indexable, i):
    """Get item from list by index"""
    try:
        return indexable[int(i)]
    except (IndexError, TypeError, ValueError):
        return None