from django import template

register = template.Library()


@register.simple_tag
def update_value(arg):
    return arg


@register.filter
def player_filter(player_skills, p_id):
    return player_skills.filter(player=p_id)
