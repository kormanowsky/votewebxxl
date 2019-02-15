from datetime import datetime, timedelta

from django import template

from ..models import Image, Voting
from ..functions import date_human, datetime_human, date_process, time_human
from VoteSimple.settings import VERSION


register = template.Library()


@register.simple_tag
def avatar(request, user=None):
    return Image.get_avatar_url(request, user)


@register.simple_tag
def formatted_date(date=None):
    return date_human(date_process(date))


@register.simple_tag
def formatted_datetime(date=None, add_at=True):
    return datetime_human(date_process(date), add_at)


@register.simple_tag
def formatted_time(date=None):
    return time_human(date_process(date))


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
def voting_added_to_favourites(voting, request, user=None):
    if not user:
        if not request.user.is_authenticated:
            return False
        user = request.user
    return voting.user_added_to_favourites(user)


@register.simple_tag
def votewebxxl_version():
    return VERSION
