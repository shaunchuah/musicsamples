import re

from django import template

register = template.Library()


@register.filter
def remove_page_param(querystring):
    return re.sub(r"&?page=\d+", "", querystring)
