from django_components import Component
from django_components import register


@register("pager")
class ThemePicker(Component):
    template_file = "pager.html"
    js_file = "pager.js"
