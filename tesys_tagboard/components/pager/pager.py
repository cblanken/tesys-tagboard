from django_components import Component
from django_components import register


@register("pager")
class PagerComponent(Component):
    template_file = "pager.html"
    js_file = "pager.js"

    def get_template_data(self, args, kwargs, slots, context):
        pager = self.kwargs.get("pager")
        page = self.kwargs.get("page")
        return {"pager": pager, "page": page}
