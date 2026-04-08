import os
from django import template
from django.conf import settings

register = template.Library()

@register.filter
def valid_avatar(avatar_field):
    """
    Trả về True nếu file avatar thực sự tồn tại.
    """
    if not avatar_field:
        return False
    
    file_path = os.path.join(settings.MEDIA_ROOT, str(avatar_field))
    return os.path.isfile(file_path)