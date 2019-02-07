from django import template
from ..models import Image

register = template.Library()

@register.simple_tag
def avatar(request, user=None):
    return Image.get_avatar_url(request, user)