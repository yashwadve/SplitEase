# Drop this file at: apps/core/templatetags/se_extras.py
# (create the templatetags/ folder + an empty __init__.py alongside it
# if your core app doesn't already have one)
#
# Then in any template: {% load se_extras %}  ...  {{ balance|abs_value }}

from django import template

register = template.Library()


@register.filter
def abs_value(value):
    """Absolute value for Decimal/int/float — used to show '-150.00' as '150.00'
    next to a pill that already says 'owe' or 'owed'."""
    try:
        return abs(value)
    except TypeError:
        return value