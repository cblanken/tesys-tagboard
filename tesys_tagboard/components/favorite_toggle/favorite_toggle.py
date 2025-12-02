from django_components import Component
from django_components import register


@register("favorite_toggle")
class FavoriteToggleComponent(Component):
    template_file = "favorite_toggle.html"
    js_file = "favorite_toggle.js"

    def get_template_data(self, args, kwargs, slots, context):
        post = kwargs.get("post")
        return {"post": post}
