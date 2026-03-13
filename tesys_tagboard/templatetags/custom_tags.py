from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(name="get_title")
def get_title() -> str:
    """Get the apps title from settings"""
    return settings.TITLE
