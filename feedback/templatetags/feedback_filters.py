# feedback/templatetags/feedback_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get item from dictionary
    Usage: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(int(key) if str(key).isdigit() else key)