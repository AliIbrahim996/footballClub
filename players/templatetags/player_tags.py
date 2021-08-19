from django import template

register = template.Library()


@register.simple_tag
def update_value(arg):
    return arg
