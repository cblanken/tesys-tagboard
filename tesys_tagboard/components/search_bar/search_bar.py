from django_components import Component
from django_components import register


@register("search_bar")
class SearchBarComponent(Component):
    template_file = "search_bar.html"
    js_file = "search_bar.js"

    def get_template_data(self, args, kwargs, slots, context):
        hidden = kwargs.get("hidden")
        input_text = kwargs.get("input_text")
        return {
            "hidden": hidden,
            "input_text": input_text,
        }
