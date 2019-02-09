from datetime import datetime, timedelta

from django import template

from ..models import Image, Voting
from ..functions import date_human



register = template.Library()

@register.simple_tag
def avatar(request, user=None):
    return Image.get_avatar_url(request, user)

@register.simple_tag
def formatted_date(date=None):
    if not date:
        date = datetime.now()
    elif date == "today":
        date = datetime.now()
    elif date == "tomorrow":
        date = datetime.now() + timedelta(days=1)
    elif date == "yesterday":
        date = datetime.now() - timedelta(days=1)
    return date_human(date)

@register.simple_tag
def voting_status(voting, request, user=None):
    if not user:
        if not request.user.is_authenticated:
            if voting.open_stats:
                return Voting.VOTING_OPEN_STATS
            else:
                return Voting.VOTING_VISIBLE
        user = request.user
    return voting.status(user)

@register.simple_tag
def votingaddedtofavourites(voting, request, user=None):
    if not user:
        if not request.user.is_authenticated:
            return False
        user = request.user
    return voting.user_added_to_favourites(user)