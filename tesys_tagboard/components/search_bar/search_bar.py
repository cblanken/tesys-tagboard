from django_components import Component
from django_components import register


@register("search_bar")
class SearchBarComponent(Component):
    template_file = "search_bar.html"
    js_file = "search_bar.js"

    def get_template_data(self, args, kwargs, slots, context):
        hidden = kwargs.get("hidden")
        return {
            "hidden": hidden,
        }
