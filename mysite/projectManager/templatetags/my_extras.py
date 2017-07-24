from django import template
import ast

register = template.Library()


@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)

@register.filter(name='return_item')
def return_item(l, i):
    try:
        return l[i]
    except:
        return None

@register.filter(name='return_prev_item')
def return_prev_item(l, i):
    try:
        return l[i - 1]
    except:
        return None

@register.filter
def list_string_to_value(string):
    try:
        return ast.literal_eval(string)
    except:
        return None



