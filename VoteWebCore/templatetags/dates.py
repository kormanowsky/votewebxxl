from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.simple_tag
def formatteddate(date=None):
    if not date:
        date = datetime.now()
    elif date == "today":
        date = datetime.now()
    elif date == "tomorrow":
        date = datetime.now() + timedelta(days=1)
    return date.strftime("%d.%m.%Y")