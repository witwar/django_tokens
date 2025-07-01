from django import template
from django.utils.safestring import mark_safe
from .. import token_parser

register = template.Library()

@register.simple_tag
def render_tokens(text, **context):
    return mark_safe(token_parser.replace_tokens(text, context))
