from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='currency')
def currency(value):
    """
    Format the value with the currency symbol from settings.
    Usage: {{ product.price|currency }}
    """
    if value is None:
        return ''
    return f'{settings.CURRENCY_SYMBOL}{value}'
