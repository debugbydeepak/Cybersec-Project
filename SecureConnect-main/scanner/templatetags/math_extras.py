from django import template

register = template.Library()

@register.filter(name='mul')
def mul(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='div')
def div(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value
