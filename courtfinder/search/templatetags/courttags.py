from django import template

from search.models import *

register = template.Library()


@register.filter
def court_opening_times_ordered(courtdict):
    """Takes a dict representing a court, return the opening times in order"""
    court = Court.objects.get(slug=courtdict["slug"])  # Would be nice if ID was included
    return [
        OpeningTime.objects.get(pk=cot.opening_time_id)
        for cot in CourtOpeningTime.objects.filter(
            court_id=court.id).order_by("sort")
    ]
