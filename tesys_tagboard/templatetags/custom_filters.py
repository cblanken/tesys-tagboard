import markdown
from django import template
from django.utils.safestring import SafeString

register = template.Library()


@register.filter(name="concat")
def concat(value, arg) -> str:
    """Concatenate string value and arg string."""
    return f"{value}{arg}"


@register.filter(name="get_item")
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name="to_int")
def to_int(s: str):
    return int(s)


@register.filter(name="markdown")
def render_markdown(content: str):
    md = markdown.Markdown(extensions=["sane_lists"])
    return SafeString(md.convert(content))
