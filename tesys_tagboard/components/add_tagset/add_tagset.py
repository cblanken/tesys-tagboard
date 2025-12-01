from django.urls import reverse
from django_components import Component
from django_components import register

from tesys_tagboard.components.tag.tag import Action


@register("add_tagset")
class AddTagsetComponent(Component):
    template_file = "add_tagset.html"
    js_file = "add_tagset.js"

    def get_template_data(self, args, kwargs, slots, context):
        size = kwargs.get("size")
        add_tag_enabled = kwargs.get("add_tag_enabled")

        data = {
            "size": size,
            "add_tag_enabled": bool(add_tag_enabled),
            "tags": kwargs.get("tags"),
            "actions": [Action("remove", "Remove this tag from the tag set", "")],
        }

        post = kwargs.get("post")
        if post:
            data |= {"post_url": reverse("post-edit", args=[post.pk])}
        return data
