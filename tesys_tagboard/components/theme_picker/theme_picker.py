from django_components import Component
from django_components import register


@register("theme_picker")
class ThemePicker(Component):
    template_file = "theme_picker.html"
    js_file = "theme_picker.js"

    def get_template_data(self, args, kwargs, slots, context):
        return {}
