from dataclasses import dataclass

from django_components import Component
from django_components import register


@dataclass
class Action:
    name: str
    desc: str
    code: str


@register("tag")
class TagComponent(Component):
    template_file = "tag.html"
    js_file = "tag.js"

    def get_template_data(self, args, kwargs, slots, context):
        tag = kwargs.get("tag")
        size = kwargs.get("size")
        category = tag.get_category_display()
        extra_actions = kwargs.get("actions", [])
        actions = [
            Action("search", "Search for posts with this tag", ""),
            *extra_actions,
        ]
        return {"tag": tag, "size": size, "category": category, "actions": actions}
