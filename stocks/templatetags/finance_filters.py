from django import template

register = template.Library()

@register.filter
def to_crore(value):
    try:
        return int(value) / 1e7
    except Exception as e:
        print(e)
        return None

@register.filter
def indian_comma(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    negative = value < 0
    value = abs(value)

    integer, dot, frac = f"{value}".partition(".")

    if len(integer) <= 3:
        result = integer
    else:
        result = integer[-3:]
        integer = integer[:-3]
        while integer:
            result = integer[-2:] + "," + result
            integer = integer[:-2]

    formatted = result + (dot + frac if frac else "")
    return f"-{formatted}" if negative else formatted
