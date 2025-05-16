from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Splits a string into a list on the given delimiter.
    """
    return value.split(arg)

@register.filter
def get_shipment_status_index(shipment):
    """
    Returns the index of the current shipment status in the standard status list.
    """
    statuses = ['order placed', 'processing', 'shipped', 'out for delivery', 'delivered']
    try:
        return statuses.index(shipment.status)
    except (ValueError, AttributeError):
        return -1