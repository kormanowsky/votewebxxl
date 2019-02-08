from django import template
from ..models import Image, Voting
from datetime import datetime, timedelta
from ..functions import is_logged_in

register = template.Library()

@register.simple_tag
def avatar(request, user=None):
    return Image.get_avatar_url(request, user)

@register.simple_tag
def formatteddate(date=None):
    if not date:
        date = datetime.now()
    elif date == "today":
        date = datetime.now()
    elif date == "tomorrow":
        date = datetime.now() + timedelta(days=1)
    elif date == "yesterday":
        date = datetime.now() - timedelta(days=1)
    return date.strftime("%d.%m.%Y")

@register.simple_tag
def votingstatus(voting, request, user=None):
    if not user:
        if not is_logged_in(request):
            if voting.open_stats:
                return Voting.VOTING_OPEN_STATS
            else:
                return Voting.VOTING_VISIBLE
        user = request.user
    return voting.status(user)