from django_components import Component
from django_components import register


@register("tag_search")
class ThemePicker(Component):
    template_file = "tag_search.html"
    js_file = "tag_search.js"

    def get_template_data(self, args, kwargs, slots, context):
        return {}
